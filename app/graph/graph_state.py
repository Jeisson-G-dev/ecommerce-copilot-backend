from langgraph.graph.message import MessagesState
from app.models.router_output import RouterOutput


class GraphState(MessagesState, total=False):
    user_input: str
    ui_context: dict
    next_node: RouterOutput  # type: ignore
