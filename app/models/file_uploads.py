from sqlalchemy import (
    Column, Integer, BigInteger, Text,
    TIMESTAMP, ForeignKey, text
)
from app.models.base import Base
from sqlalchemy.orm import relationship

class FileUpload(Base):
    __tablename__ = "file_uploads"
    __table_args__ = {"schema": "dev"}

    upload_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("dev.users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("dev.client_profiles.client_id", ondelete="RESTRICT"),
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
        ForeignKey("dev.users.user_id", ondelete="RESTRICT"),
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

    user = relationship("User", back_populates="uploads", foreign_keys=[user_id])
    client = relationship("ClientProfile", back_populates="uploads")
