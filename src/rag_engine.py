import os
from typing import List, Optional, Annotated


class ScannedPDFError(ValueError):
    """PDF sin texto extraíble (escaneado o basado en imágenes)."""
from langchain_qdrant import QdrantVectorStore # Cambiado de Qdrant a QdrantVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg # Añadido InjectedToolArg
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import pytesseract
from pdf2image import convert_from_path
from src.database import update_vectorization_progress
from src.config import settings

# --- Configuración de Base de Datos Vectorial ---

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = FastEmbedEmbeddings(model_name=settings.embedding_model)
    return _embeddings

def get_vector_store(collection_name: str = "knowledge_base"):
    url = settings.qdrant_url
    api_key = settings.qdrant_api_key
    
    client = QdrantClient(url=url, api_key=api_key)

    # Auto-create collection if it doesn't exist (BAAI/bge-small-en-v1.5 → 384 dims)
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=get_embeddings()
    )
    return vector_store

@tool
def search_in_documents(query_text: str, config: Annotated[RunnableConfig, InjectedToolArg]): # Renombrado de knowledge_retriever y query
    """
    Busca en los documentos PDF subidos por el usuario en esta sesión.
    Úsala cuando el usuario pregunte sobre el contenido de un documento,
    pida resumir, analizar o extraer información de archivos cargados.
    """
    try:
        session_id = config.get("configurable", {}).get("thread_id", "default")
        print(f"DEBUG: Tool search_in_documents called with session_id: {session_id}, query: {query_text}")
        store = get_vector_store()
        from qdrant_client.http import models
        
        # Construimos un filtro robusto e inclusivo para la sesión actual
        # Buscamos 'session_id' tanto en la raíz como dentro del objeto metadata tradicional.
        # Esto soluciona problemas de discrepancia entre versiones de langchain-qdrant.
        qdrant_filter = models.Filter(
            must=[
                models.Filter(
                    should=[
                        models.FieldCondition(key="session_id", match=models.MatchValue(value=session_id)),
                        models.FieldCondition(key="metadata.session_id", match=models.MatchValue(value=session_id)),
                    ]
                )
            ]
        )
        
        print(f"DEBUG: Using filter for session_id: {session_id}")
        docs = store.similarity_search(query_text, k=5, filter=qdrant_filter)
        # Ordenar por posición en el documento para que el LLM reciba contexto en orden
        docs.sort(key=lambda d: d.metadata.get("chunk_index", 0))
        results = "\n---\n".join([d.page_content for d in docs])
        print(f"DEBUG: Tool found {len(docs)} documents WITH filter")
        return f"Contenido relevante de documentos (Sesión: {session_id}):\n{results}"
    except Exception as e:
        print(f"DEBUG: ERROR in search_in_documents: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al buscar en documentos: {str(e)}"

def process_pdf(file_path: str, session_id: str = "default"):
    """
    Lee un archivo PDF, lo divide en fragmentos e indexa en Qdrant asociados a un session_id.
    Actualiza el progreso en la base de datos.
    """
    try:
        update_vectorization_progress(session_id, "processing", 10)
        print(f"DEBUG: Processing PDF {file_path} for session_id: {session_id}")

        # Deduplication: skip if this exact filename is already vectorized for this session
        source_name = os.path.basename(file_path)
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        if client.collection_exists("knowledge_base"):
            from qdrant_client.http import models as qdrant_models
            existing, _ = client.scroll(
                collection_name="knowledge_base",
                scroll_filter=qdrant_models.Filter(must=[
                    qdrant_models.Filter(should=[
                        qdrant_models.FieldCondition(key="session_id", match=qdrant_models.MatchValue(value=session_id)),
                        qdrant_models.FieldCondition(key="metadata.session_id", match=qdrant_models.MatchValue(value=session_id)),
                    ]),
                    qdrant_models.Filter(should=[
                        qdrant_models.FieldCondition(key="source", match=qdrant_models.MatchValue(value=source_name)),
                        qdrant_models.FieldCondition(key="metadata.source", match=qdrant_models.MatchValue(value=source_name)),
                    ]),
                ]),
                limit=1,
                with_payload=False,
            )
            if existing:
                print(f"DEBUG: '{source_name}' already vectorized for session {session_id}, skipping.")
                update_vectorization_progress(session_id, "completed", 100)
                return 0

        reader = PdfReader(file_path)
        text = ""
        total_pages = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
            text += page.extract_text()
            # Actualizamos progreso de extracción (hasta el 30%)
            if i % 10 == 0 or i == total_pages - 1:
                prog = 10 + int((i / total_pages) * 20)
                update_vectorization_progress(session_id, "processing", prog)

        print(f"DEBUG: Extracted {len(text)} characters from PDF")

        if not text.strip():
            print(f"DEBUG: No text layer found — attempting OCR fallback for {os.path.basename(file_path)}")
            update_vectorization_progress(session_id, "processing", 15)
            try:
                images = convert_from_path(file_path, dpi=settings.ocr_dpi)
                ocr_parts = []
                for idx, img in enumerate(images):
                    page_text = pytesseract.image_to_string(img, lang="spa+eng")
                    ocr_parts.append(page_text)
                    prog = 15 + int(((idx + 1) / len(images)) * 15)
                    update_vectorization_progress(session_id, "processing", prog)
                text = "\n".join(ocr_parts)
                print(f"DEBUG: OCR extracted {len(text)} characters from {len(images)} pages")
            except Exception as ocr_err:
                print(f"DEBUG: OCR failed: {ocr_err}")

        if not text.strip():
            msg = f"'{os.path.basename(file_path)}' no contiene texto extraíble (ni texto embebido ni OCR)."
            print(f"DEBUG: {msg}")
            update_vectorization_progress(session_id, "failed", 0)
            raise ScannedPDFError(msg)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        chunks = text_splitter.split_text(text)
        print(f"DEBUG: Created {len(chunks)} chunks")
        
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "source": os.path.basename(file_path),
                    "session_id": session_id,
                    "chunk_index": i,
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        if not documents:
            update_vectorization_progress(session_id, "completed", 100)
            return 0

        # --- BATCH PROCESSING (Embeddings) ---
        store = get_vector_store()
        batch_size = 50
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            store.add_documents(batch)
            
            # Actualizamos progreso (del 30% al 100%)
            current_batch = i // batch_size + 1
            prog = 30 + int((current_batch / total_batches) * 70)
            update_vectorization_progress(session_id, "processing", min(prog, 99))
            print(f"DEBUG: Processed batch {current_batch}/{total_batches}")

        update_vectorization_progress(session_id, "completed", 100)
        print(f"DEBUG: Successfully added {len(documents)} docs to Qdrant")
        return len(documents)
        
    except ScannedPDFError:
        raise  # DB ya está en "failed", no re-escribir
    except Exception as e:
        print(f"DEBUG: ERROR in process_pdf: {str(e)}")
        update_vectorization_progress(session_id, "failed", 0)
        raise e
