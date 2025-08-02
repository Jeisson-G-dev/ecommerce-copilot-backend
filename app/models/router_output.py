from pydantic import BaseModel
from typing import Literal


# Lista estática de nodos válidos (basado en config.NODES actual)
NextNodeLiteral = Literal[
    "advisor_node",
    "guide_node",
    "tooltip_node",
]

class RouterOutput(BaseModel):
    next_node: NextNodeLiteral