from sqlalchemy import (
    Column, Integer, BigInteger, Text,
    TIMESTAMP, ForeignKey, text
)
from app.models.base import Base

class FileUpload(Base):
    __tablename__ = "file_uploads"

    upload_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("client_profiles.client_id", ondelete="RESTRICT"),
        nullable=False
    )

    original_filename = Column(Text, nullable=False)
    s3_saved_filename = Column(Text, nullable=False)

    file_size = Column(BigInteger, nullable=False)

    uploaded_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    notes = Column(Text)
    s3_saved_path = Column(Text, nullable=False)

    uploaded_by = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
