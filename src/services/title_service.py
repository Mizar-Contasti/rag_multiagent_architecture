from langchain_groq import ChatGroq
from src.config import settings

def generate_chat_title(text: str) -> str:
    """
    Generates a 3-5 word title for a chat session based on provided text (first message or document snippet).
    """
    if not text or len(text.strip()) < 5:
        return "Nuevo Chat"
    
    try:
        model = ChatGroq(
            model=settings.default_fast_model,
            api_key=settings.groq_api_key,
            temperature=0.1,
        )
        
        prompt = (
            "Genera un título corto y descriptivo (máximo 5 palabras) para una conversación que comienza con este texto. "
            "Responde ÚNICAMENTE con el título, sin comillas ni puntos finales.\n\n"
            f"Texto: {text[:500]}"
        )
        
        response = model.invoke(prompt)
        title = response.content.strip()
        
        # Cleanup if LLM ignores instructions
        if title.startswith("Título:") or title.startswith("Title:"):
            title = title.split(":", 1)[1].strip()
            
        return title[:50] # Safety limit
    except Exception as e:
        print(f"DEBUG: Error generating title: {e}")
        return "Nuevo Chat"
