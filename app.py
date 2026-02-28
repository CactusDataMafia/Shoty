import rumps
import AppKit 
from util import delete_before, del_for_a_specific_date
class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super().__init__("Awesome App")
    
        delete_menu = rumps.MenuItem(title="Delete", key="C")
        delete_menu.add(rumps.MenuItem("Delete for a specific day", callback=self.delete_for_day))
        delete_menu.add(rumps.MenuItem("Delete before N days", callback=self.delete_before_days))
        self.menu = [delete_menu]

    def delete_for_day(self, _):
        AppKit.NSApp.activateIgnoringOtherApps_(True)
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

    def delete_before_days(self, _):
        AppKit.NSApp.activateIgnoringOtherApps_(True)
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


if __name__ == "__main__":
    AwesomeStatusBarApp().run()