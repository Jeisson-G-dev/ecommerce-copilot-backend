from typing import List
from pydantic import BaseModel
from app.models.tooltip_output import TooltipPopup

class GuideOutput(BaseModel):
    response: str
    popups: List[TooltipPopup]

