import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Document(BaseModel):
    id: uuid.UUID
    related_entity_id: uuid.UUID
    related_entity_type: str
    document_type: str
    filename: str
    # The s3_path is internal and not exposed. We'll expose a download URL instead.
    download_url: str
    created_at: datetime

    class Config:
        orm_mode = True

class PresignedUploadURL(BaseModel):
    upload_url: str
    s3_path: str
