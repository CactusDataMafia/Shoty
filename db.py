import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


APP_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "Shoty"
APP_SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
DB_NAME = str(APP_SUPPORT_DIR / "ScreenShots.db")
TABLE_NAME = "ScreenShots"

@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_NAME, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA journal_mode=WAL;')
    connection.execute('PRAGMA synchronous=NORMAL;')
    try:
        yield connection
    finally:
        connection.close()

def init_db():
    with get_connection() as connection:
        cursor = connection.cursor()

        db_creation_command = """
        CREATE TABLE IF NOT EXISTS ScreenShots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creation_date TEXT NOT NULL,
        path TEXT NOT NULL UNIQUE,
        filename TEXT NOT NULL
        );
        """

        cursor.execute(db_creation_command)
        connection.commit()

def add_to_db(db_connection, file_path_obj):
    db_cursor = db_connection.cursor()

    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    absolute_path = str(file_path_obj.resolve())
    file_name = file_path_obj.name

    command = f"INSERT INTO {TABLE_NAME} (creation_date, path, filename) VALUES (?, ?, ?)"
    
    try:
        db_cursor.execute(command, (creation_date, absolute_path, file_name))
        db_connection.commit()
    except Exception as e:
        pass

def clear_db():
    with get_connection() as connection:
        connection.execute(f"DELETE FROM {TABLE_NAME}")
        connection.commit()

def sync_db(path):
    path_obj = Path(path)
    if not path_obj.is_dir():
        raise NotADirectoryError("Данный путь не видет в директорию!\nДля корректной работы необходимо указать путь до директории")

    with get_connection() as connection:
        cursor = connection.cursor()
        
        command = f"INSERT OR IGNORE INTO {TABLE_NAME} (creation_date, path, filename) VALUES (?, ?, ?)"

        for child in path_obj.iterdir():
            if not child.is_dir():
                creation_time = datetime.fromtimestamp(child.stat().st_birthtime).strftime("%Y-%m-%d %H:%M:%S")
                absolute_path = str(child.resolve())
                file_name = child.name
                cursor.execute(command, (creation_time, absolute_path, file_name))
        connection.commit()
