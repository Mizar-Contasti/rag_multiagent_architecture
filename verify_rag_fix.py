
import os
import asyncio
import uuid
import sys

# Añadir el directorio raíz al path para importar src
sys.path.append(os.getcwd())

from src.rag_engine import search_in_documents, process_pdf, get_vector_store
from langchain_core.runnables import RunnableConfig

async def test_rag_isolation_and_retrieval():
    print("\n--- INICIANDO TEST DE RAG (AISLAMIENTO Y RECUPERACIÓN) ---")
    
    session_a = f"test-session-A-{uuid.uuid4().hex[:6]}"
    session_b = f"test-session-B-{uuid.uuid4().hex[:6]}"
    
    # Crear un archivo temporal para simular un documento
    test_file_path = "test_document.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("El código secreto de la Sesión A es: ANTIGRAVITY-123. Este documento solo debe ser visible en la Sesión A.")
    
    # Qdrant suele necesitar PDFs, pero process_pdf usa PdfReader. 
    # Para el test, vamos a insertar directamente usando el store si es posible, 
    # o simplemente verificar que el filtro de búsqueda funcione.
    
    from langchain_core.documents import Document
    store = get_vector_store()
    
    print(f"DEBUG: Insertando documento de prueba en Sesión A: {session_a}")
    doc_a = Document(
        page_content="El código secreto de la Sesión A es: ANTIGRAVITY-123. Este documento solo debe ser visible en la Sesión A.",
        metadata={"session_id": session_a, "source": "test_a.pdf"}
    )
    store.add_documents([doc_a])
    
    # 1. Test: Búsqueda en Sesión A (Debe encontrarlo)
    print(f"TEST 1: Buscando en Sesión A...")
    config_a = {"configurable": {"thread_id": session_a}}
    result_a = search_in_documents.invoke({"query_text": "código secreto"}, config=config_a)
    
    if "ANTIGRAVITY-123" in result_a:
        print("✅ ÉXITO: Sesión A recuperó su propio documento.")
    else:
        print("❌ FALLO: Sesión A no encontró su documento.")
        print(f"Resultado: {result_a}")

    # 2. Test: Búsqueda en Sesión B (NO debe encontrar nada de A)
    print(f"TEST 2: Buscando en Sesión B (Aislamiento)...")
    config_b = {"configurable": {"thread_id": session_b}}
    result_b = search_in_documents.invoke({"query_text": "código secreto"}, config=config_b)
    
    if "ANTIGRAVITY-123" not in result_b:
        print("✅ ÉXITO: Sesión B está aislada de los datos de la Sesión A.")
    else:
        print("❌ FALLO: ¡Fuga de datos! Sesión B encontró información de la Sesión A.")
        print(f"Resultado: {result_b}")

    # Limpieza (opcional, Qdrant es persistente pero esto ayuda a validar)
    print("\n--- TEST FINALIZADO ---")

if __name__ == "__main__":
    asyncio.run(test_rag_isolation_and_retrieval())
