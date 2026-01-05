from datetime import datetime
from typing import Optional
from .base import ORMBase

class FileUploadCreate(ORMBase):
    client_id: int
    original_filename: str
    s3_saved_filename: str
    file_size: int
    s3_saved_path: str
    notes: Optional[str] = None

class FileUploadRead(ORMBase):
    upload_id: int
    client_id: int
    original_filename: str
    s3_saved_filename: str
    file_size: int
    uploaded_at: datetime

class FileUploadUpdate(ORMBase):
    notes: Optional[str] = None
