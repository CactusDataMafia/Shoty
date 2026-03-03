from pathlib import Path
from datetime import datetime, timedelta, date
from collections import defaultdict
import json
from db import get_connection, TABLE_NAME, APP_SUPPORT_DIR

CONFIG_PATH = APP_SUPPORT_DIR / "config.json"


### Functions to work with data and time

def count_file_creation_time(file: Path):
    return datetime.fromtimestamp(file.stat().st_birthtime)

def count_timedelta(file: Path) -> timedelta:
    return datetime.now() - count_file_creation_time(file)

def parse_user_date(user_date: str) -> date:
    year, month, day = [int(el) for el in user_date.split("-")]
    return date(year=year, day=day, month=month)


### Functions to work with DB

def get_screen_last_7_days():
    with get_connection() as connection:
        cursor = connection.cursor()

        command = f"SELECT DATE(creation_date) as day, COUNT(*) as count FROM {TABLE_NAME} WHERE creation_date >= DATE('now', '-7 days') GROUP BY DATE(creation_date) ORDER BY DATE(creation_date) DESC"
        data = cursor.execute(command).fetchall()
        return data
    
def get_all_screenshots():
    with get_connection() as connection:
        cursor = connection.cursor()
    
        command = f"SELECT * FROM {TABLE_NAME}"
        data = cursor.execute(command)
        return data.fetchall()

def show_amount_screens():
    with get_connection() as connection:
        cursor = connection.cursor()

        command = f"SELECT COUNT(*) FROM {TABLE_NAME}"
        amount = cursor.execute(command).fetchone()[0]
        return int(amount)

def group_by_day(screenshots) -> dict[date, list[Path]]:
    screenshot_per_days = defaultdict(list)
    for screen in screenshots:
        path_obj = Path(screen["path"])
        screenshot_date = datetime.strptime(screen["creation_date"], "%Y-%m-%d %H:%M:%S").date()
        screenshot_per_days[screenshot_date].append(path_obj)
    return screenshot_per_days

def delete_before(days: int) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        threshold_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        command = f"SELECT * FROM {TABLE_NAME} WHERE creation_date < ?"
        data = cursor.execute(command, (threshold_date, )).fetchall()

        for screen in data:
            path_obj = Path(screen["path"])
            try:
                path_obj.unlink()
            except FileNotFoundError:
                print(f"Error: File '{path_obj.name}' not found.")
            except PermissionError:
                print(f"Error: Permission denied to delete file '{path_obj.name}'.")
            else:
                cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE path = ?", (str(path_obj),))
                print("Files have been succesfull deleted.")
        connection.commit()

def find_screens_for_a_specific_date(user_date: str):
        with get_connection() as connection:
            cursor = connection.cursor()
            user_date_obj = parse_user_date(user_date)
            user_datetime = datetime(year=user_date_obj.year, month=user_date_obj.month, day=user_date_obj.day).strftime("%Y-%m-%d %H:%M:%S")
            command = f"SELECT * FROM {TABLE_NAME} WHERE DATE(creation_date) = DATE(?)"
            data = cursor.execute(command, (user_datetime, )).fetchall()
            return data
        
def del_for_a_specific_date(user_date):
    with get_connection() as connection:
        cursor = connection.cursor()
        screens_for_date = find_screens_for_a_specific_date(user_date)
        for screen in screens_for_date:
            path_obj = Path(screen["path"])
            try:
                path_obj.unlink()
            except FileNotFoundError:
                print(f"Error: File '{path_obj.name}' not found.")
            except PermissionError:
                print(f"Error: Permission denied to delete file '{path_obj.name}'.")
            else:
                cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE path = ?", (str(path_obj),))
                print("Files have been succesfull deleted.")
        connection.commit()

### Files to work with config

def create_empty_config():
    CONFIG_PATH.write_text("{}", encoding="utf-8")

def update_config_dict(new_path: str):
    path_obj = Path(new_path)
    if not path_obj.is_dir():
        raise NotADirectoryError("Данный путь не видет в директорию!\nДля корректной работы необходимо указать путь до директории")

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config["screenshot_dir"] = new_path
    CONFIG_PATH.write_text(json.dumps(config), encoding="utf-8")

def update_notification_time(new_time: str):
    try:
        hours, minutes = [int(el) for el in new_time.split(":")]
    except TypeError:
        raise

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config["notification_time"] = new_time
    CONFIG_PATH.write_text(json.dumps(config), encoding="utf-8")

def load_config() -> dict | None:
    if CONFIG_PATH.exists():
        try:
            config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return config
        except:
            return None
    return None