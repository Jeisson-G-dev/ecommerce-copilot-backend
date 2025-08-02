from app.graph.graph_state import GraphState
from app.graph.llm import llm
from app.config import config
from app.models.router_output import RouterOutput
from app.models.tooltip_output import TooltipOutput
from langchain_core.messages import AIMessage
import json
from logger import logger

SYSTEM_MESSAGE = """
Eres un agente experto en experiencia de usuario que guía al usuario mediante tooltips interactivos.

Tu tarea es identificar qué elemento visual (DOM target) de la página debe ser resaltado o explicado al usuario, y generar una guía paso a paso adecuada.

La estructura de respuesta **DEBE** ser en formato JSON con los siguientes campos:

- response: breve texto de respuesta conversacional al usuario.
- popup:
    - type: siempre debe ser "info".
    - target: uno de los valores de los grupos disponibles en "availableTargets" (productos, navegación o filtros).
    - title: título breve para el tooltip.
    - message: explicación corta para el usuario.
    - targetInfo: objeto con un campo ID. Si se refiere a un producto, el ID es el del producto afectado; si no aplica, usa ID=1.

Responde con un solo paso por vez. Si el usuario menciona múltiples elementos, responde solo uno con la mayor prioridad.

Ejemplos:
- Usuario: "Resalta el botón para agregar al carrito"
→ target: product_button

- Usuario: "Dónde están los filtros de precio?"
→ target: price_filter

- Usuario: "Muéstrame cómo volver al home"
→ target: home

No expliques. Solo devuelve el JSON con la guía.

NOTA: Devuelve todos los campos como objetos JSON reales, sin strings serializados. No uses comillas para los diccionarios internos.

Ejemplo de respuesta:
{
  "response": "Haz clic aquí para agregar al carrito",
  "popup": {
    "type": "guide-step",
    "target": "product_button",
    "title": "Agregar al Carrito",
    "message": "Haz clic en este botón para agregar el producto",
    "targetInfo": {
      "ID": 1
    }
  }
}

"""

def tooltip_node(state: GraphState) -> GraphState:
    """
    Nodo que genera una guía visual (tooltip) basada en el contexto y mensaje del usuario.
    """
    logger.info("Ejecutando tooltip_node")
    structured_llm = llm.with_structured_output(TooltipOutput)

    user_message = {
        "role": "user",
        "content": (
            f"Mensaje del usuario: {state['user_input']}\n\n"
            f"Contexto de UI:\n{json.dumps(state['ui_context'], ensure_ascii=False, indent=2)}"
        )
    }

    system_message = {"role": "system", "content": SYSTEM_MESSAGE}

    response = structured_llm.invoke([system_message, user_message])
    logger.info("Respuesta del LLM: %s", response)

    return {
        **state,
        "messages": state.get("messages", []) + [
            AIMessage(
                content=response.response,
                additional_kwargs={"popup": response.popup.model_dump()}
            )
        ],
    }