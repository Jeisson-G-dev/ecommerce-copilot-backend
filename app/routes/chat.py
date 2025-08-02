from fastapi import APIRouter, status
from app.graph.main_graph import run_graph
from app.models.request_model import NewChat
from logger import logger

chat_router = APIRouter()

@chat_router.post(
    "/chat",
    summary="Chat con el asistente",
    status_code=status.HTTP_200_OK,
)
def assistant(request: NewChat):
    """
    Procesa un mensaje del usuario a través del grafo de conversación.

    Args:
        request (NewChat): Objeto que contiene el mensaje y el ID del usuario.

    Returns:
        Dict[str, Any]: Última respuesta generada por el asistente.
    """
    try:
        response = run_graph(request.userInput, request.uiContext)
        last_message = response.get("messages", [])[-1]

        # Contenido principal
        result = {"response": last_message.content}

        # Si hay campos adicionales (como `popup`), los incluimos
        if hasattr(last_message, "additional_kwargs") and last_message.additional_kwargs:
            result.update(last_message.additional_kwargs)

        return result

    except Exception as e:
        logger.error(
            "Error al procesar la solicitud de chat",
            exc_info=True
        )
        return {"error": f"Error interno del servidor: {str(e)}"}
