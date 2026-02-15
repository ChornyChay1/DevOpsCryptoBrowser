from sqlalchemy import Column, String, Integer
from core.db import Base

class IndicatorDB(Base):
    __tablename__ = "indicators"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    period = Column(Integer, nullable=False)
