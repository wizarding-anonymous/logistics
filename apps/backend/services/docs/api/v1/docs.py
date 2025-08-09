import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service
from ...database import get_db

router = APIRouter()

@router.get("/documents/upload-url", response_model=schemas.PresignedUploadURL)
async def get_upload_url_endpoint(
    entity_type: str = Query(..., description="Type of the entity (e.g., 'order')"),
    entity_id: uuid.UUID = Query(..., description="ID of the entity"),
    filename: str = Query(..., description="The name of the file to be uploaded"),
):
    """
    Get a presigned URL to upload a file directly to S3.
    """
    result = await service.get_upload_url(entity_type, entity_id, filename)
    if not result:
        raise HTTPException(status_code=500, detail="Could not generate upload URL")
    return result

@router.post("/documents/register", response_model=schemas.Document)
async def register_document_endpoint(
    s3_path: str,
    entity_type: str,
    entity_id: uuid.UUID,
    document_type: str,
    filename: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a document's metadata after it has been successfully uploaded to S3.
    """
    # In a real app, we might want to verify the file exists at the s3_path
    # before creating the DB record.
    db_doc = await service.register_document(db, s3_path, entity_type, entity_id, document_type, filename)

    # We need to return a schema with a download URL, so we fetch it again
    return await service.get_document_with_download_url(db, db_doc.id)


@router.get("/documents/entity/{entity_type}/{entity_id}", response_model=List[schemas.Document])
async def list_documents_for_entity_endpoint(
    entity_type: str,
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    List all documents associated with a specific entity.
    """
    db_docs = await service.list_documents_for_entity(db, entity_type, entity_id)

    # We need to generate a download URL for each document
    response_docs = []
    for doc in db_docs:
        doc_with_url = await service.get_document_with_download_url(db, doc.id)
        if doc_with_url:
            response_docs.append(doc_with_url)

    return response_docs

@router.get("/documents/{document_id}", response_model=schemas.Document)
async def get_document_endpoint(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single document's metadata, including a fresh presigned download URL.
    """
    doc = await service.get_document_with_download_url(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
