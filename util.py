from pathlib import Path
from datetime import datetime, timedelta, date
from collections import defaultdict
import json

CONFIG_PATH = Path(__file__).parent / "config.json"

def count_file_creation_time(file: Path):
    return datetime.fromtimestamp(file.stat().st_birthtime)

def count_timedelta(file: Path) -> timedelta:
    return datetime.now() - count_file_creation_time(file)

def group_by_day(screenshot_dir: Path) -> dict[date, list[Path]]:
    screenshot_per_days = defaultdict(list)
    for child in screenshot_dir.iterdir():
        screenshot_date = count_file_creation_time(child).date()
        screenshot_per_days[screenshot_date].append(child)
    return screenshot_per_days

def get_valid_dates(screenshot_dict, days: int, ) -> list[date]:
    threshold_date: date = (datetime.now() - timedelta(days=days)).date() #
    screen_dates = sorted(screenshot_dict.keys(), reverse=True)
    last_valid_date_indx = 0
    for indx, dt in enumerate(screen_dates):
        dt: date
        if dt < threshold_date:
            last_valid_date_indx = indx
            break
    
    return screen_dates[last_valid_date_indx:]

def delete_before(screenshot_dir: Path, days: int) -> None:
    screen_dict = group_by_day(screenshot_dir)
    dates_to_delete = get_valid_dates(screen_dict, days)
    for dt in dates_to_delete:
        for screen in screen_dict[dt]:
            try:
                screen.unlink()
            except FileNotFoundError:
                print(f"Error: File '{screen.name}' not found.")
            except PermissionError:
                print(f"Error: Permission denied to delete file '{screen.name}'.")
            else:
                print("Files have been succesfull deleted.")

def pretty_output(screen_per_days_dict) -> None:
    for indx, dict_data in enumerate(sorted(screen_per_days_dict.items(), reverse=True)):
        print(f"{indx}. {dict_data[0]} - {len(dict_data[1])} screenshots")

def show_files_per_day(screenshot_dict, user_date) -> None:
    screens_for_a_day = screenshot_dict[user_date]
    for indx, screen in enumerate(screens_for_a_day):
        print(f"{indx}. {screen.name}")

def parse_user_date(user_date: str) -> date:
    year, month, day = [int(el) for el in user_date.split("-")]
    return date(year=year, day=day, month=month)

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

def settings():
    return setup()

def del_for_a_specific_date(screenshot_dir, user_date: date):
    screen_dict = group_by_day(screenshot_dir)
    screens_for_a_day = screen_dict[user_date]
    for screen in screens_for_a_day:
            try:
                screen.unlink()
            except FileNotFoundError:
                print(f"Error: File '{screen.name}' not found.")
            except PermissionError:
                print(f"Error: Permission denied to delete file '{screen.name}'.")
            else:
                print("Files have been succesfull deleted.")