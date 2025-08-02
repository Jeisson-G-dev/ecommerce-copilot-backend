from app.graph.graph_state import GraphState
from app.graph.llm import llm
from app.models.guide_output import GuideOutput
from langchain_core.messages import AIMessage
import json
from logger import logger

SYSTEM_MESSAGE = """
Eres un agente experto en experiencia de usuario que guía al usuario mediante una secuencia de tooltips interactivos.

Tu tarea es identificar los pasos necesarios que el usuario debe seguir en la interfaz para completar una acción, y generar una guía visual paso a paso.

La estructura de respuesta DEBE ser un JSON como el siguiente:

NOTA: el type debe ser siempre "guide-step".

{
  "response": "Te guiaré paso a paso para agregar la Camiseta Básica de Algodón al carrito.",
  "popups": [
    {
      "type": "guide-step",
      "target": "product",
      "title": "Seleccionar producto",
      "message": "Haz clic en el producto para ver sus detalles.",
      "targetInfo": { "ID": 1 }
    },
    {
      "type": "guide-step",
      "target": "product_button",
      "title": "Agregar al carrito",
      "message": "Haz clic aquí para agregar el producto seleccionado al carrito.",
      "targetInfo": { "ID": 1 }
    },
    {
      "type": "guide-step",
      "target": "cart",
      "title": "Ir al carrito",
      "message": "Haz clic en el ícono del carrito para revisar tu compra.",
      "targetInfo": { "ID": 1 }
    }
  ]
}

No expliques. No pongas el JSON como string. Devuelve el objeto JSON directamente.
"""

def guide_node(state: GraphState) -> GraphState:
    """
    Nodo que genera una guía completa con múltiples tooltips para llevar al usuario por una tarea.
    """
    structured_llm = llm.with_structured_output(GuideOutput)

    user_message = {
        "role": "user",
        "content": (
            f"Mensaje del usuario: {state['user_input']}\n\n"
            f"Contexto de UI:\n{json.dumps(state['ui_context'], ensure_ascii=False, indent=2)}"
        )
    }

    system_message = {"role": "system", "content": SYSTEM_MESSAGE}

    response = structured_llm.invoke([system_message, user_message])
    logger.info("Respuesta del LLM (guía): %s", response)

    return {
        **state,
        "messages": state.get("messages", []) + [
            AIMessage(
                content=response.response,
                additional_kwargs={
                    "steps": [popup.model_dump() for popup in response.popups]
                }
            )
        ],
    }
