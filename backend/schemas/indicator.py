from pydantic import BaseModel

class IndicatorCreate(BaseModel):
    name: str
    period: int


class IndicatorUpdate(BaseModel):
    name: str | None = None
    period: int | None = None
