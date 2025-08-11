from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from ... import service

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def search_endpoint(q: str):
    """
    Performs a site-wide search across multiple indices.
    """
    # TODO: Add authentication/authorization if needed
    # TODO: Add pagination
    return service.search_documents(query=q)
