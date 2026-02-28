from pathlib import Path
from datetime import datetime, timedelta, date
from collections import defaultdict
import json
from db import get_connection, TABLE_NAME

CONFIG_PATH = Path(__file__).parent / "config.json"
### Functions to work with data and time

def count_file_creation_time(file: Path):
    return datetime.fromtimestamp(file.stat().st_birthtime)

def count_timedelta(file: Path) -> timedelta:
    return datetime.now() - count_file_creation_time(file)

def parse_user_date(user_date: str) -> date:
    year, month, day = [int(el) for el in user_date.split("-")]
    return date(year=year, day=day, month=month)


### Functions to work with DB

def get_all_screenshots():
    with get_connection() as connection:
        cursor = connection.cursor()
    
        command = f"SELECT * FROM {TABLE_NAME}"
        data = cursor.execute(command)
        return data.fetchall()

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

def del_for_a_specific_date(user_date: str):
    with get_connection() as connection:
        cursor = connection.cursor()
        user_date_obj = parse_user_date(user_date)
        user_datetime = datetime(year=user_date_obj.year, month=user_date_obj.month, day=user_date_obj.day).strftime("%Y-%m-%d %H:%M:%S")
        command = f"SELECT * FROM {TABLE_NAME} WHERE DATE(creation_date) = DATE(?)"
        data = cursor.execute(command, (user_datetime, )).fetchall()

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

### Files to work with config

def setup():
    screenshot_dir = input("Введите путь до папки со скриншотами: ")
    if not Path(screenshot_dir).is_dir():
        raise NotADirectoryError("Данный путь не видет в директорию!\nДля корректной работы необходимо указать путь до директории")
    
    notification_time = input("Время уведомления (например 21:00): ")

    config = {
        "screenshot_dir": screenshot_dir,
        "notification_time": notification_time
    }

    CONFIG_PATH.write_text(json.dumps(config), encoding="utf-8")
    
    return config

def load_config() -> dict:
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return config
    else:
        return setup()


### Function not using now

# def pretty_output(screen_per_days_dict) -> None:
#     for indx, dict_data in enumerate(sorted(screen_per_days_dict.items(), reverse=True)):
#         print(f"{indx}. {dict_data[0]} - {len(dict_data[1])} screenshots")

# def show_files_per_day(screenshot_dict, user_date) -> None:
#     screens_for_a_day = screenshot_dict[user_date]
#     for indx, screen in enumerate(screens_for_a_day):
#         print(f"{indx}. {screen.name}")

# def settings():
#     return setup()

# def get_valid_dates(screenshot_dict, days: int, ) -> list[date]:
#     threshold_date: date = (datetime.now() - timedelta(days=days)).date() #
#     screen_dates = sorted(screenshot_dict.keys(), reverse=True)
#     last_valid_date_indx = 0
#     for indx, dt in enumerate(screen_dates):
#         dt: date
#         if dt < threshold_date:
#             last_valid_date_indx = indx
#             break
    
#     return screen_dates[last_valid_date_indx:]