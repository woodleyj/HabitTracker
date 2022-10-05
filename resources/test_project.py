from starter import starter_habits
from database import DBConn
from datetime import datetime
import os


class TestHabits:

    def setup_class(self):
        # Create the test database and populate with starter habit information and history
        self.db = DBConn(name="test.db")
        starter_habits(db_name="test.db")

    def test_add_record(self):
        self.db.add_record(["Test Habit", "Test Desc", "Daily", datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "0", "0"])

    def test_complete_task(self):
        self.db.complete_task("Test Habit")

    def test_delete_record(self):
        self.db.delete_record("Updated Test Habit")

    def test_display_habit_name(self):
        self.db.get_habit_names()

    def test_get_history(self):
        self.db.get_history("Test Habit")

    def test_get_interval(self):
        self.db.get_interval("Test Habit")

    def test_get_interval_habits(self):
        self.db.get_interval_habits("Daily")
        self.db.get_interval_habits("Weekly")

    def test_get_longest_streak(self):
        # Test to get the longest streak overall
        self.db.get_longest_streak()

    def test_get_longest_streak_selected_habit(self):
        # Test to get the longest streak of specific habit
        self.db.get_longest_streak("Test Habit")

    def test_update_record(self):
        self.db.update_record("Test Habit", "name", "Updated Test Habit")

    def test_update_streak(self):
        # Test to increment streak counter
        self.db.update_streak("Drink Water")
        # Test to reset streak counter
        self.db.update_streak("Drink Water", reset_streak=True)

    def teardown_class(self):
        self.db.conn.close()  # Produces sqlite3 Error, but if I don't include this line then db doesn't delete
        os.remove("test.db")
