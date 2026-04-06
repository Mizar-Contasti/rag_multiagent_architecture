import uuid
from src.orchestrator import create_orchestrator
from langchain_core.messages import HumanMessage

def run_agent_interaction(user_input: str):
    """
    Ejecuta el grafo de agentes y maneja la persistencia y HITL.
    """
    app = create_orchestrator()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    # Input inicial
    input_state = {"messages": [HumanMessage(content=user_input)]}
    
    # Ejecución iterativa para manejar interrupciones
    for event in app.stream(input_state, config=config, stream_mode="values"):
        last_message = event["messages"][-1]
        
        # Mostrar pensamientos de los agentes
        if hasattr(last_message, "content") and last_message.content:
            print(f"\n[Agente]: {last_message.content}")
        
    # Verificar si el estado está interrumpido (HITL)
    snapshot = app.get_state(config)
    if snapshot.next:
        print("\n--- [INTERRUPCIÓN: APROBACIÓN REQUERIDA] ---")
        print(f"La siguiente acción es: {snapshot.next}")
        print("El agente planea usar las siguientes herramientas:")
        for tool_call in snapshot.values["messages"][-1].tool_calls:
            print(f"- {tool_call['name']}({tool_call['args']})")
        
        # Aquí en una app real preguntaríamos al usuario. Simulamos aprobación.
        # input("Presiona Enter para continuar...")
        # app.invoke(None, config=config) # Continúa desde donde se detuvo

if __name__ == "__main__":
    print("Iniciando Orquestador Multi-Agente...")
    query = "Investiga cuáles son las 3 noticias más importantes de IA hoy y genera un resumen profesional."
    run_agent_interaction(query)
