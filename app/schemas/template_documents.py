from datetime import datetime
from .base import ORMBase
from typing import Optional


class TemplateDocumentCreate(ORMBase):
    name: str
    template_type: str
    file_s3_location: str
    description: str | None = None

class TemplateDocumentRead(ORMBase):
    template_id: int
    name: str
    template_type: str
    file_s3_location: str
    created_time: datetime

class TemplateDocumentUpdate(ORMBase):
    name: Optional[str] = None
    template_type: Optional[str] = None
    file_s3_location: Optional[str] = None
    description: Optional[str] = None
