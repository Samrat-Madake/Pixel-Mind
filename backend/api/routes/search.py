from fastapi import APIRouter, Query
from typing import List, Optional
from backend.search.search_engine import search_engine

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
async def get_search(
    q: Optional[str] = Query(None, description="Search query string"),
    k: int = Query(50, description="Number of results to return")
):
    results = search_engine.search(query=q, k=k)
    return results
