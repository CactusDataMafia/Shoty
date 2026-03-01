import rumps
import subprocess

from watchdog.observers import Observer

from util import delete_before, del_for_a_specific_date, load_config, update_config_dict, update_notification_time, show_amount_screens, create_empty_config, find_screens_for_a_specific_date, get_screen_last_7_days
from db import sync_db, init_db, clear_db
from watcher import MyHandler

class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super().__init__("Awesome App")
        self.config = load_config()
        self.total_amount = rumps.MenuItem("Total: 0 screenshots", callback=None)

        if self.config is None:
            create_empty_config()
            self.config = self.run_setup()
            init_db()
        
        if self.config: 
            cnfg = self.config["screenshot_dir"] # type ingnore
            sync_db(cnfg)
            self.start_observer(cnfg)

        
        self.update_total_display()


        overview_menu = rumps.MenuItem(title="Overview", key="O")
        overview_menu.add(self.total_amount)
        overview_menu.add(rumps.MenuItem("Show last 7 days", callback=self.show_last_7_days))
        overview_menu.add(rumps.MenuItem("Show specific day", callback=self.show_screens_for_a_day))

        delete_menu = rumps.MenuItem(title="Delete", key="D")
        delete_menu.add(rumps.MenuItem("Delete for a specific day", callback=self.delete_for_day))
        delete_menu.add(rumps.MenuItem("Delete before N days", callback=self.delete_before_days))

        settings_menu = rumps.MenuItem(title="Settings", key="S")
        settings_menu.add(rumps.MenuItem("Change screenshot directory", callback=self.change_dir))
        settings_menu.add(rumps.MenuItem("Change notification time", callback=self.change_time))
        
        self.menu = [overview_menu, delete_menu, settings_menu]

    def run_setup(self):
        
        while True:
            window = rumps.Window(
                message="It's your first touch with Shoty\nEnter absolute path to screenshots directory: ",
                title="Setup screenshots directory location",
                ok="Save",
                cancel="Cancel"
            )
            response = window.run()

            if not response.clicked:
                rumps.quit_application()
                return

            path = response.text.strip()
            try:
                update_config_dict(path)
                break
            except NotADirectoryError:
                rumps.alert("Error", "Path do not provide to directory! Retry")
        
        while True:
            window = rumps.Window(
                message="Enter notification time (e.g. 21:00):",
                title="Setup notification time",
                default_text="21:00"
            )
            response = window.run()

            if not response.clicked:
                rumps.quit_application()
                return

            time_val = response.text.strip()
            try:
                update_notification_time(time_val)
                break
            except TypeError:
                rumps.alert("Error", "Unsopported time format! Use HH:MM")

        return load_config()

    def start_observer(self, path):
        observer = Observer()
        observer.schedule(MyHandler(on_new_file=self.update_total_display), path=path, recursive=False)
        observer.daemon = True
        observer.start()
        self.observer = observer

    def update_total_display(self):
        
        count = show_amount_screens()
        self.total_amount.title = f"Total: {count} screenshots"


### MenuItems Callbacks ###

    ### Overview menu ###

    def show_screens_for_a_day(self, _):
        
        window = rumps.Window(
            message="Enter date (YYYY-MM-DD): ",
            title="Show screenshots for a day",
            ok="Enter",
            cancel="Cancel"
        )

        response = window.run()
        if response.clicked and response.text.strip():
            user_date = response.text.strip()
            screens = find_screens_for_a_specific_date(user_date)
            files = [screen["path"] for screen in screens]
            if not files:
                rumps.alert("No screenshots found for this date")
                return
            subprocess.run(["qlmanage", "-p"] + files)

    def show_last_7_days(self, _):
        data = get_screen_last_7_days()
        if not data:
            lines = "No screenshots in the last 7 days"
        else:
            lines = "\n".join(f"{row["day"]}: {row["count"]} screenshots" for row in data)
        subprocess.run(["osascript", "-e", f'display dialog "{lines}" buttons {{"OK"}} with title "Last 7 days"'])
        

    ### Delete menu ###

    def delete_for_day(self, _):

        window = rumps.Window(
            message="Enter date (YYYY-MM-DD): ",
            title="Delete for a specific day",
            ok="Delete",
            cancel="Cancel"
        )

        response = window.run()
        if response.clicked and response.text.strip():
            user_date = response.text.strip()
            del_for_a_specific_date(user_date)
            self.update_total_display()

    def delete_before_days(self, _):

        window = rumps.Window(
            message="Enter a number",
            title="Delete before N day",
            ok="Delete",
            cancel="Cancel"
        )

        response = window.run()
        if response.clicked and response.text.strip():
            days = int(response.text.strip())
            delete_before(days)
            self.update_total_display()


    ### Settings menu ###

    def change_dir(self, _):
        window = rumps.Window(
            message="Enter absolute path to screenshots directory: ",
            title="Change screenshots directory location",
            ok="Save",
            cancel="Cancel"
        )

        response = window.run()
        if response.clicked and response.text.strip():
            user_path = response.text.strip()
            try:
                update_config_dict(user_path)
            except NotADirectoryError:
                rumps.alert("Error", "Path does not lead to a directory!")
                return
            
            self.config = load_config()

            self.observer.stop()
            self.observer.join()
            clear_db()
            sync_db(user_path)
            self.start_observer(user_path)
            self.update_total_display()

    
    def change_time(self, _):
        window = rumps.Window(
            message="Enter notification time: ",
            title="Change notification time",
            ok="Save",
            cancel="Cancel"
        )

        response = window.run()
        if response.clicked and response.text.strip():
            user_path = response.text.strip()
            update_notification_time(user_path)
            self.config = load_config()

if __name__ == "__main__":
    AwesomeStatusBarApp().run()