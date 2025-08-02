from pydantic import BaseModel
from typing import Literal, Optional, Dict

from pydantic import field_validator
import json

class TooltipPopup(BaseModel):
    type: Literal["guide-step"]
    target: str
    title: str
    message: str
    targetInfo: Dict[str, int]

    @field_validator("targetInfo", mode="before")
    @classmethod
    def parse_target_info(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("targetInfo debe ser un dict o un string JSON válido")
        return value

class TooltipOutput(BaseModel):
    response: str
    popup: TooltipPopup