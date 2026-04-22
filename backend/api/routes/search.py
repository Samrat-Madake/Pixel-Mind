from fastapi import APIRouter, Query
from typing import List, Optional
from backend.search.search_engine import search_engine

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
async def get_search(
    q: Optional[str] = Query(None, description="Search query string"),
    date_from: Optional[str] = Query(None, description="Start date"),
    date_to: Optional[str] = Query(None, description="End date"),
    camera_make: Optional[str] = Query(None, description="Camera make"),
    camera_model: Optional[str] = Query(None, description="Camera model"),
    location: Optional[str] = Query(None, description="Location name"),
    person: Optional[str] = Query(None, description="Person name"),
    k: int = Query(50, description="Number of results to return")
):
    filters = {
        "date_from": date_from,
        "date_to": date_to,
        "camera_make": camera_make,
        "camera_model": camera_model,
        "location": location
    }
    results = search_engine.search(query=q, filters=filters, person=person, k=k)
    return results
