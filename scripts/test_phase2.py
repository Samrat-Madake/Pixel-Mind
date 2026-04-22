import asyncio
import sys
import os
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.pipelines.ingest import ingest_module
from backend.db.db import init_db, get_db_connection
from backend.search.faiss_store import faiss_clip, faiss_face

async def run_test(folder_path):
    print("Script file loaded")
    
    # Ensure database tables exist before processing
    init_db()
    
    print(f"--- Phase 2 Test: Ingesting {folder_path} ---")
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Path {folder_path} does not exist.")
        return

    # 1. Trigger Ingestion
    print("Starting ingestion...")
    count = await ingest_module.add_to_queue(folder_path)
    print(f"Added {count} files to queue.")
    
    # Give it a second to start
    await asyncio.sleep(1)
    
    # Wait for processing to complete
    while ingest_module.is_processing or not ingest_module.queue.empty():
        print(f"Progress: {ingest_module.processed_count}/{ingest_module.total_count} processed...")
        await asyncio.sleep(5) # Give it more time between logs
        
    print("\n" + "="*40)
    print("       FINAL PHASE 2 REPORT")
    print("="*40)
    
    # 2. Database Verification
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT count(*) FROM images")
    img_count = cursor.fetchone()[0]
    print(f"Total images in DB:      {img_count}")
    
    cursor.execute("SELECT count(*) FROM faces")
    face_count = cursor.fetchone()[0]
    print(f"Total faces detected:    {face_count}")
    
    cursor.execute("SELECT count(*) FROM duplicates")
    dup_count = cursor.fetchone()[0]
    print(f"Duplicate pairs found:   {dup_count}")
    
    cursor.execute("SELECT id, file_path, sha256 FROM images LIMIT 5")
    print("\n--- Sample Records (from DB) ---")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Hash: {row[2][:10]}... | Path: {os.path.basename(row[1])}")
        
    conn.close()
    
    # 3. FAISS Verification
    print(f"\n--- Vector Storage ---")
    print(f"CLIP vectors (512-D): {faiss_clip.index.ntotal}")
    print(f"Face vectors (128-D): {faiss_face.index.ntotal}")
    
    # 4. Thumbnail Verification
    thumb_dir = Path("data/thumbnails")
    thumbs = list(thumb_dir.glob("*.jpg"))
    print(f"Thumbnails generated: {len(thumbs)}")
    print("="*40)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_phase2.py <folder_path>")
    else:
        print("Main started")
        asyncio.run(run_test(sys.argv[1]))
