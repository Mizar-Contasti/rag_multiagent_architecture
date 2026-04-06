
import os
import asyncio
import uuid
import sys

# Añadir el directorio raíz al path para importar src
sys.path.append('.')

from src.services.chat_service import run_chat
from src.rag_engine import get_vector_store
from langchain_core.documents import Document

async def benchmark_models():
    # Modelos a testear de Groq
    models = [
        "qwen-2.5-32b",        # Representando Gwen
        "llama-3.1-70b-versatile", # Representando Llama 3.1b (o similar de alto rendimiento)
        "llama-3.3-70b-specdec",    # Representando Llama 3.3 70b
        "llama-3.2-11b-vision-preview" # Representando Llama 4 (o similar de nueva generación)
    ]
    
    sess_id = f"bench-{uuid.uuid4().hex[:4]}"
    print(f"\n--- INICIANDO BENCHMARK DE MODELOS (SESIÓN: {sess_id}) ---\n")
    
    # Pre-cargar documento en el RAG para esta sesión
    store = get_vector_store()
    doc = Document(
        page_content="El proyecto ANTIGRAVITY es un sistema de propulsión iónica de quinta generación que utiliza kriptón como combustible.",
        metadata={"session_id": sess_id, "source": "proyecto_secreto.pdf"}
    )
    store.add_documents([doc])
    print(f"Documento de prueba inyectado: 'Proyecto ANTIGRAVITY'\n")
    
    results = {}
    
    for model in models:
        print(f"Probando Modelo: {model}...")
        try:
            # Simulamos la pregunta del usuario
            response = await run_chat(
                message="De que trata el proyecto Antigravity según el documento?",
                thread_id=sess_id,
                model_name=model
            )
            
            reply = response.get("reply", "")
            agent = response.get("agent", "unknown")
            
            # Verificaciones
            has_think = "<think>" in reply.lower()
            is_rag_ok = "propulsión iónica" in reply.lower() or "kriptón" in reply.lower()
            
            results[model] = {
                "reply_preview": reply[:100] + "...",
                "agent_used": agent,
                "clean_of_think": not has_think,
                "rag_success": is_rag_ok
            }
            
            status = "✅ OK" if is_rag_ok and not has_think else "⚠️ ERROR"
            print(f"   Status: {status} | Agente: {agent} | Clean: {not has_think} | RAG: {is_rag_ok}\n")
            
        except Exception as e:
            print(f"   ❌ ERROR al invocar {model}: {e}\n")
            results[model] = {"error": str(e)}

    print("\n--- RESUMEN DEL BENCHMARK ---")
    for m, r in results.items():
        if "error" in r:
            print(f"- {m}: FALLO CRÍTICO ({r['error']})")
        else:
            print(f"- {m}: RAG={r['rag_success']}, Clean={r['clean_of_think']}, Agent={r['agent_used']}")

if __name__ == "__main__":
    asyncio.run(benchmark_models())
