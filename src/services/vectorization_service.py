from fastapi import BackgroundTasks
from src.database import update_vectorization_progress
from src.rag_engine import process_pdf


def _run_process_pdf(file_path: str, session_id: str):
    """Wrapper that absorbs exceptions so background task errors don't crash ASGI.
    The DB status is already set to 'failed' inside process_pdf before any raise."""
    try:
        process_pdf(file_path, session_id=session_id)
    except Exception as e:
        print(f"DEBUG: Background PDF task ended with error (DB already updated): {e}")


def start_vectorization(file_path: str, session_id: str, background_tasks: BackgroundTasks):
    """Set initial progress and enqueue PDF processing as a background task."""
    update_vectorization_progress(session_id, "processing", 10)
    background_tasks.add_task(_run_process_pdf, file_path, session_id)
