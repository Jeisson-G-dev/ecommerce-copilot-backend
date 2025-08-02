from pydantic import BaseModel
from typing import Any, Dict


class NewChat(BaseModel):
    userInput: str
    uiContext: Dict[str, Any]