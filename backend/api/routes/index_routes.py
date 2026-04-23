from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from backend.pipelines.ingest import ingest_module
from backend.api.sse import sse_manager
import asyncio

router = APIRouter(prefix="/index", tags=["index"])

class IndexRequest(BaseModel):
    folder_path: str

# Forward ingest module progress to SSE queue
async def ingest_with_progress(folder_path: str):
    count = ingest_module.scan_folder(folder_path)
    if not count:
        await sse_manager.add_event("index", {"status": "error", "message": "Folder not found or no valid images."})
        return

    ingest_module.total_count += len(count)
    for file in count:
        await ingest_module.queue.put(file)
    
    if not ingest_module.is_processing:
        # We need a custom runner to hook into sse
        ingest_module.is_processing = True
        asyncio.create_task(run_ingest_loop())
        await sse_manager.add_event("index", {"status": "started", "total": ingest_module.total_count})

async def run_ingest_loop():
    # Modified from ingest.py to include SSE emissions
    # Because ingest.process_queue doesn't emit SSE by default in current code
    # We will just patch the queue consumption or let the ingest module run and poll progress
    # But polling is easier and less intrusive for now.
    import time
    
    # Trigger original process_queue
    task = asyncio.create_task(ingest_module.process_queue())
    
    last_processed = -1
    while not task.done():
        if ingest_module.processed_count != last_processed:
            last_processed = ingest_module.processed_count
            pct = 0
            if ingest_module.total_count > 0:
                pct = int((last_processed / ingest_module.total_count) * 100)
            
            await sse_manager.add_event("index", {
                "status": "processing",
                "processed": last_processed,
                "total": ingest_module.total_count,
                "pct": pct
            })
        await asyncio.sleep(0.5)
        
    await sse_manager.add_event("index", {
        "status": "done",
        "processed": ingest_module.processed_count,
        "total": ingest_module.total_count,
        "pct": 100
    })

@router.post("/")
async def start_indexing(req: IndexRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_with_progress, req.folder_path)
    return {"message": "Indexing started", "folder": req.folder_path}

@router.get("/progress")
async def get_progress():
    return StreamingResponse(sse_manager.stream_events("index"), media_type="text/event-stream")

@router.get("/status")
async def get_status():
    status = "idle"
    if ingest_module.is_processing:
        status = "indexing"
    elif ingest_module.total_count > 0 and ingest_module.processed_count >= ingest_module.total_count:
        status = "completed"
        
    current_step = status
    if status == "indexing" and hasattr(ingest_module, 'current_file') and ingest_module.current_file:
        import os
        filename = os.path.basename(ingest_module.current_file)
        current_step = f"Processing: {filename}"
        
    return {
        "status": status,
        "processed_items": ingest_module.processed_count,
        "total_items": ingest_module.total_count,
        "current_step": current_step
    }
