from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any, Optional

from ... import service

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def search_endpoint(
    q: str,
    status: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
):
    """
    Performs a site-wide search with optional filters.
    """
    return service.search_documents(
        query=q,
        status=status,
        min_price=min_price,
        max_price=max_price
    )
