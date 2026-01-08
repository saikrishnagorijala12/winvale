from pydantic import BaseModel
from datetime import datetime

class ORMBase(BaseModel):
    class Config:
        from_attributes = True
