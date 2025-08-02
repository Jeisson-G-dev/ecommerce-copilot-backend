from app.graph.graph_state import GraphState
from app.graph.llm import llm
from app.models.router_output import RouterOutput
from langchain_core.messages import AIMessage
import json
#guide_node: El usuario está buscando información sobre un producto, una categoría o una característica específica, necesita encontrar algo o saber cómo se hace


SYSTEM_MESSAGE = """Tu tarea es clasificar la intención del siguiente mensaje del usuario en uno de los siguientes tipos:

advisor_node: si el usuario está haciendo una pregunta, buscando recomendaciones o recibiendo asistencia general.
tooltip_node: si el usuario solicita que se resalte algo, menciona elementos de la interfaz, habla de tooltips o sugiere una acción visual.

Ejemplos:
- "¿Cuál me recomiendas?" → advisor
- "Resalta la camiseta negra" → tooltip
- "¿Qué producto es mejor?" → advisor
- "Quiero que marques las camisas azules" → tooltip
"""

def router_node(state: GraphState) -> GraphState:
    """
    Clasifica la intención del usuario y decide el siguiente nodo del grafo.
    """
    structured_llm = llm.with_structured_output(RouterOutput)

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {
            "role": "user",
            "content": f"""
                Mensaje del usuario: {state['user_input']}
                Contexto de UI: {json.dumps(state['ui_context'], ensure_ascii=False, indent=2)}
            """
        }
    ]

    response = structured_llm.invoke(messages)

    return {
        **state,
        "next_node": response.next_node,
        "messages": state.get("messages", []) + [
            AIMessage(content=f"Clasificación: {response.next_node}")
        ],
    }