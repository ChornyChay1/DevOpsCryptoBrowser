from pydantic import BaseModel
from utils.constants import Indicators
from typing import Optional
class IndicatorCreate(BaseModel):
    name: str
    type: Indicators
    period: int


class IndicatorUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Indicators] = None
    period: Optional[int] = None
