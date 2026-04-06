import uuid
from src.database import (
    list_sessions,
    get_session,
    create_session,
    update_session,
    delete_session,
)


def get_all_sessions():
    return list_sessions()


def create_new_session(id: str, title: str, selected_model: str):
    create_session(id, title, selected_model)


def update_existing_session(session_id: str, **kwargs):
    # Translate frontend camelCase to DB snake_case
    if "selectedModel" in kwargs:
        kwargs["selected_model"] = kwargs.pop("selectedModel")
    update_session(session_id, **kwargs)


def delete_existing_session(session_id: str):
    delete_session(session_id)


def get_vectorization_status(session_id: str) -> dict:
    session = get_session(session_id)
    if not session:
        return {"status": "idle", "progress": 0}
    return {
        "status": session.get("vectorizationStatus", "idle"),
        "progress": session.get("vectorizationProgress", 0),
    }


def persist_chat_exchange(thread_id: str, user_text: str, reply: str, agent_name: str):
    """Append a user+assistant message pair to the session's message history in DB."""
    sessions_by_id = {s["id"]: s for s in list_sessions()}
    current_messages = sessions_by_id.get(thread_id, {}).get("messages", [])
    current_messages.append({"id": str(uuid.uuid4()), "text": user_text, "sender": "user"})
    current_messages.append({"id": str(uuid.uuid4()), "text": reply, "sender": "assistant", "agent": agent_name})
    update_session(thread_id, messages=current_messages)
