import asyncio
import os
import shutil
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time
import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("api_audit")

from src.database import init_db
from src.rag_engine import get_embeddings
from src.orchestrator import init_memory
from src.config import settings
from src.services.session_service import (
    get_all_sessions,
    create_new_session,
    update_existing_session,
    delete_existing_session,
    get_vectorization_status,
    persist_chat_exchange,
)
from src.services.vectorization_service import start_vectorization
from src.services.chat_service import run_chat

app = FastAPI(title="Multi-Agent Chat-with-PDF API")

# --- Audit Middleware ---
@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log request details for auditing
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        f"AUDIT: {client_host} | {request.method} {request.url.path} | "
        f"Status: {response.status_code} | Time: {process_time:.3f}s"
    )
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    init_memory()
    os.makedirs(settings.upload_dir, exist_ok=True)
    print("DEBUG: Pre-heating embeddings model...")
    get_embeddings()
    print("DEBUG: Embeddings model ready.")


# --- Session endpoints ---

@app.get("/sessions")
def get_sessions():
    return get_all_sessions()


class SessionCreate(BaseModel):
    id: str
    title: str
    selectedModel: str = settings.default_model


@app.post("/sessions", status_code=201)
def post_session(body: SessionCreate):
    create_new_session(body.id, body.title, body.selectedModel)
    return {"id": body.id}


class SessionUpdate(BaseModel):
    messages: Optional[list] = None
    documents: Optional[list] = None
    title: Optional[str] = None
    selectedModel: Optional[str] = None


@app.patch("/sessions/{session_id}")
def patch_session(session_id: str, body: SessionUpdate):
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    update_existing_session(session_id, **kwargs)
    return {"ok": True}


@app.delete("/sessions/{session_id}", status_code=204)
def del_session(session_id: str):
    delete_existing_session(session_id)


@app.get("/sessions/{session_id}/status")
def get_session_status(session_id: str):
    return get_vectorization_status(session_id)


# --- Upload endpoint ---

MAX_UPLOAD_BYTES = settings.max_upload_mb * 1024 * 1024


@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form("default"),
):
    # Validate file type (backend-side, not just frontend accept)
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF (.pdf)")

    # Read with size limit (read MAX+1 to detect overflow without loading full file)
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo excede el límite de {settings.max_upload_mb}MB",
        )

    safe_name = os.path.basename(filename)
    file_path = os.path.join(settings.upload_dir, safe_name)
    with open(file_path, "wb") as f:
        f.write(content)

    start_vectorization(file_path, session_id, background_tasks)

    return {
        "filename": safe_name,
        "session_id": session_id,
        "message": f"El archivo se está procesando en segundo plano para la sesión {session_id}.",
    }


# --- Chat endpoint ---

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None
    model: str = settings.default_fast_model
    is_first_message: bool = False


@app.post("/chat")
async def chat_with_agents(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    generated_title = None

    # Si es el primer mensaje, generamos un título inteligente
    if request.is_first_message:
        from src.services.title_service import generate_chat_title
        generated_title = generate_chat_title(request.message)
        update_existing_session(thread_id, title=generated_title)

    try:
        result = await asyncio.wait_for(
            run_chat(request.message, thread_id, request.model),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="El agente tardó demasiado en responder. Intenta de nuevo.",
        )
    
    persist_chat_exchange(thread_id, request.message, result["reply"], result["agent"])
    
    if generated_title:
        result["generated_title"] = generated_title
        
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
