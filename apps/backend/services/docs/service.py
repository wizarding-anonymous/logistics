import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models, schemas, s3_client

async def get_upload_url(entity_type: str, entity_id: uuid.UUID, filename: str):
    """
    Generates a presigned URL for a client to upload a file to S3.
    """
    # Create a unique path for the object in S3
    object_name = f"{entity_type}/{entity_id}/{uuid.uuid4()}/{filename}"

    upload_url = s3_client.create_presigned_upload_url(object_name)

    if upload_url:
        return schemas.PresignedUploadURL(upload_url=upload_url, s3_path=object_name)
    return None

async def register_document(db: AsyncSession, s3_path: str, entity_type: str, entity_id: uuid.UUID, document_type: str, filename: str):
    """
    Creates a document metadata record in the database after a file has been uploaded.
    """
    db_doc = models.Document(
        related_entity_id=entity_id,
        related_entity_type=entity_type,
        document_type=document_type,
        filename=filename,
        s3_path=s3_path
    )
    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)
    return db_doc

async def list_documents_for_entity(db: AsyncSession, entity_type: str, entity_id: uuid.UUID):
    """
    Lists all documents associated with a specific entity.
    """
    result = await db.execute(
        select(models.Document)
        .where(
            models.Document.related_entity_type == entity_type,
            models.Document.related_entity_id == entity_id
        )
    )
    return result.scalars().all()

async def get_document_with_download_url(db: AsyncSession, document_id: uuid.UUID):
    """
    Retrieves a document and generates a presigned download URL for it.
    """
    db_doc = await db.get(models.Document, document_id)
    if not db_doc:
        return None

    download_url = s3_client.create_presigned_download_url(db_doc.s3_path)

    # We can't directly add the download_url to the ORM object, so we create a schema instance
    return schemas.Document(
        id=db_doc.id,
        related_entity_id=db_doc.related_entity_id,
        related_entity_type=db_doc.related_entity_type,
        document_type=db_doc.document_type,
        filename=db_doc.filename,
        download_url=download_url,
        created_at=db_doc.created_at
    )
