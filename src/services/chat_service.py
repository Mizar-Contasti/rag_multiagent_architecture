import time
import re
from langchain_core.messages import HumanMessage
from src.orchestrator import create_orchestrator


async def run_chat(message: str, thread_id: str, model_name: str) -> dict:
    """Invoke the multi-agent orchestrator and return the final reply."""
    orchestrator = create_orchestrator(model_name=model_name)
    config = {"configurable": {"thread_id": thread_id}}

    print(f"DEBUG: Invoking orchestrator for thread_id: {thread_id}")
    start_time = time.time()

    result = orchestrator.invoke(
        {"messages": [HumanMessage(content=message)], "model_name": model_name},
        config=config,
    )

    duration = time.time() - start_time
    print(f"DEBUG: Orchestrator execution finished in {duration:.2f}s")

    # Buscar el último mensaje con contenido real (evita AIMessages vacíos con solo tool_calls)
    last_message = next(
        (m for m in reversed(result["messages"]) if getattr(m, "content", "") and not getattr(m, "tool_calls", None)),
        result.get("messages", [None])[-1],
    )
    
    content = getattr(last_message, "content", "") if last_message else ""
    
    # Clean up any internal thoughts (like <think>...</think>) from models like Qwen/DeepSeek
    clean_reply = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    
    agent_name = result.get("next_step", "analyst")

    return {
        "reply": clean_reply or "Lo siento, no pude generar una respuesta clara.",
        "thread_id": thread_id,
        "agent": agent_name,
        "execution_time": round(duration, 2),
        "model": model_name
    }
