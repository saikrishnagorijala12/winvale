from datetime import datetime
from .base import ORMBase

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
