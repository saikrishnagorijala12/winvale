from datetime import datetime
from .base import ORMBase

class FileUploadCreate(ORMBase):
    vendor_id: int
    original_filename: str
    s3_saved_filename: str
    file_size: int
    s3_saved_path: str
    notes: str | None = None

class FileUploadRead(ORMBase):
    upload_id: int
    vendor_id: int
    original_filename: str
    s3_saved_filename: str
    file_size: int
    uploaded_at: datetime
