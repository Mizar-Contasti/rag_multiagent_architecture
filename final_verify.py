
import os
import asyncio
import uuid
import sys

# Add root dir to sys.path
sys.path.append('.')

from src.rag_engine import search_in_documents, get_vector_store
from langchain_core.documents import Document

async def test():
    sess_a = 'T-A-' + uuid.uuid4().hex[:4]
    sess_b = 'T-B-' + uuid.uuid4().hex[:4]
    
    print(f"DEBUG: Testing with Session A: {sess_a} and Session B: {sess_b}")
    
    store = get_vector_store()
    
    # Add doc to session A
    doc = Document(
        page_content='GOLDEN-TICKET-A-123', 
        metadata={'session_id': sess_a, 'source': 'test_a.pdf'}
    )
    store.add_documents([doc])
    
    # Test retrieval in A
    res_a = search_in_documents.invoke(
        {'query_text': 'GOLDEN'}, 
        {'configurable': {'thread_id': sess_a}}
    )
    is_a_ok = 'GOLDEN-TICKET-A-123' in res_a
    
    # Test isolation in B
    res_b = search_in_documents.invoke(
        {'query_text': 'GOLDEN'}, 
        {'configurable': {'thread_id': sess_b}}
    )
    is_b_isolated = 'GOLDEN-TICKET-A-123' not in res_b
    
    print(f"RESULT_A_FOUND: {is_a_ok}")
    print(f"RESULT_B_ISOLATED: {is_b_isolated}")
    
    if is_a_ok and is_b_isolated:
        print("✅ SUCCESS: RAG Isolation and Retrieval works perfectly.")
    else:
        print("❌ FAILURE: Retrieval or Isolation failed.")

if __name__ == "__main__":
    asyncio.run(test())
