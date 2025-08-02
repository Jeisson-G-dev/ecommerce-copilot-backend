from fastapi import HTTPException
from app.graph.nodes.router_node import router_node
from app.graph.nodes.advisor_node import advisor_node
from app.graph.nodes.tooltip_node import tooltip_node
from typing import Literal

from dotenv import load_dotenv

from app.graph.graph_state import GraphState
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from logger import logger

load_dotenv()

ROUTER_NODE = "router_node"
ADVISOR_NODE= "advisor_node"
TOOLTIP_NODE= "tooltip_node"

def select_agent(state: GraphState) -> Literal["advisor_node", "tooltip_node"]:
    return state["next_node"]

builder = StateGraph(GraphState)

builder.add_node(ROUTER_NODE, router_node)
builder.set_entry_point(ROUTER_NODE)

builder.add_node(ADVISOR_NODE, advisor_node)

builder.add_node(TOOLTIP_NODE, tooltip_node)


builder.add_conditional_edges(ROUTER_NODE, select_agent)

builder.add_edge(ADVISOR_NODE, END)
builder.add_edge(TOOLTIP_NODE, END)


def run_graph(user_input: str, uiContext: str):
    """
    Ejecuta el grafo de conversación con la entrada del usuario.

    Args:
        user_input (str): Mensaje del usuario.
        user_id (str): ID del usuario.

    Returns:
        dict: Resultado de la ejecución del grafo.

    Raises:
        HTTPException: Si ocurre un error en la ejecución o si el mensaje está vacío.
    """
    try:
        
        graph = builder.compile()
        graph.get_graph().draw_mermaid_png(output_file_path="flow.png")
        logger.info("user_input: %s", user_input)
        logger.info("uiContext: %s", uiContext)
        res = graph.invoke({
            "user_input": user_input,
            "ui_context": uiContext,
        })
        return res
    except Exception as e:
        logger.error("Error al ejecutar el grafo", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))