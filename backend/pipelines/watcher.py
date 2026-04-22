import os
import time
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.pipelines.ingest import ingest_module
from backend.api.sse import sse_manager
from threading import Thread

class PhotoWatcherHandler(FileSystemEventHandler):
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def _is_image(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in self.ALLOWED_EXTENSIONS

    def _trigger_ingest(self, path):
        if self._is_image(path):
            print(f"File watcher detected new/modified image: {path}")
            # We need to run the async add_to_queue in the main event loop
            asyncio.run_coroutine_threadsafe(
                self._enqueue_file(path),
                self.loop
            )

    async def _enqueue_file(self, path):
        await ingest_module.queue.put(path)
        ingest_module.total_count += 1
        
        # Start processing loop if not already running
        if not ingest_module.is_processing:
            from backend.api.routes.index_routes import run_ingest_loop
            ingest_module.is_processing = True
            asyncio.create_task(run_ingest_loop())
            await sse_manager.add_event("index", {"status": "started", "total": ingest_module.total_count})

    def on_created(self, event):
        if not event.is_directory:
            self._trigger_ingest(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._trigger_ingest(event.src_path)


class PhotoWatcher:
    def __init__(self):
        self.observer = None
        self.watch_thread = None
        self.folders = set()
        
    def start(self, folders: list, loop=None):
        if self.observer is not None:
            self.stop()
            
        if not loop:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # If no loop is running, this might fail, need a valid loop
                pass
                
        self.observer = Observer()
        handler = PhotoWatcherHandler(loop)
        
        for folder in folders:
            if os.path.exists(folder):
                self.folders.add(folder)
                self.observer.schedule(handler, folder, recursive=True)
                
        if self.folders:
            self.observer.start()
            print(f"File watcher started on: {self.folders}")
            
    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("File watcher stopped")

# Global instance
photo_watcher = PhotoWatcher()
