from watchdog.events import DirCreatedEvent, FileCreatedEvent, FileSystemEventHandler
from pathlib import Path
from db import add_to_db, get_connection


class MyHandler(FileSystemEventHandler):
    def __init__(self, on_new_file=None):
        super().__init__()
        self.on_new_file = on_new_file

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        if event.is_directory:
            return None
        src_path = event.src_path
        if isinstance(src_path, str):
            file_path = Path(src_path)
        else:
            raise TypeError(f"Unexpected src_path type: {type(src_path)}")
        with get_connection() as conn:
            add_to_db(conn, file_path)
        if self.on_new_file:
            self.on_new_file()
