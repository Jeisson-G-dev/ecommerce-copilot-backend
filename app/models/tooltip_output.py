from pydantic import BaseModel
from typing import Literal, Dict, Union

from pydantic import field_validator
import json

class TooltipPopup(BaseModel):
    type: Literal["guide-step", "info"]
    target: str
    title: str
    message: str
    targetInfo: Union[Dict[str, int], str]

    @field_validator("targetInfo", mode="before")
    @classmethod
    def parse_target_info(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v.replace("'", '"'))  # <- convierte comillas simples
            except Exception as e:
                raise ValueError("targetInfo debe ser un dict o un string JSON válido")
        raise ValueError("targetInfo debe ser un dict o un string JSON válido")

class TooltipOutput(BaseModel):
    response: str
    popup: TooltipPopup