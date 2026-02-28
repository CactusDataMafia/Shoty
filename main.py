from pathlib import Path
from util import (count_file_creation_time, group_by_day, delete_before, pretty_output,
                  parse_user_date, show_files_per_day, load_config, del_for_a_specific_date, settings)
from watchdog.observers import Observer
from watcher import MyHandler
from db import init_db, DB_NAME
import questionary


def main(screenshot_dir):
   
    start_action = questionary.select(message="Select action", choices=["overview", "delete", "settings"]).ask()
    screenshot_dir_obj = Path(screenshot_dir)
    if start_action == "delete":
        del_action = questionary.select(message="Select del type", choices=["delete for a specific day", 
                                                                            "delete before a specific day"]).ask()
        if del_action == "delete before a specific day":
            days = int(questionary.text("Enter number").ask())
            delete_before(screenshot_dir_obj, days)
        elif del_action == "delete for a specific day":
            user_date = parse_user_date(questionary.text("Enter date (in format: YYYY-MM-DD)").ask())
            del_for_a_specific_date(screenshot_dir_obj, user_date)

    elif start_action == "settings":
        settings()
    
    elif start_action == "overview":
        screenshot_db = group_by_day(screenshot_dir_obj)
        pretty_output(screenshot_db)

        answer = questionary.confirm("Do you wanna see screen for a specific date?").ask()
        if answer:
            user_date = parse_user_date(questionary.text("Enter date (YYYY-MM-DD)").ask())
            show_files_per_day(screenshot_db, user_date)

if __name__ == "__main__":
    init_db()
    config: dict = load_config()
    screenshot_dir = config["screenshot_dir"]
    
    observer = Observer()
    observer.schedule(MyHandler(), screenshot_dir, recursive=False)
    observer.start()

    try:
        ...
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
    # main(screenshot_dir)
