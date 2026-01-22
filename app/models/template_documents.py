from sqlalchemy import Column, Integer, Text, TIMESTAMP, text
from app.models.base import Base

class TemplateDocument(Base):
    __tablename__ = "template_documents"

    template_id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(Text, nullable=False)
    description = Column(Text)

    template_type = Column(Text, nullable=False)
    file_s3_location = Column(Text, nullable=False)

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
