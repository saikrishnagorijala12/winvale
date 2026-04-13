from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
