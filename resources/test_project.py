import sqlite3

from database import DBConn
import os


class TestDB:

    def setup_class(self):
        self.db = DBConn(name="test.db")
        self.db.starter_habits()

    def test_add_record(self):
        self.db.add_record("Test Habit", "Test Desc", "Daily")

    def test_get_interval(self):
        self.db.get_interval("Test Habit")

    def test_complete_task(self):
        self.db.complete_task("Test Habit")

    def test_fetch_habit_history(self):
        self.db.get_history("Test Habit")

    def test_fetch_longest(self):
        self.db.get_longest_streak("Test Habit")

    def test_update_record(self):
        self.db.update_record("Test Habit", "name", "Updated Test Habit")

    def test_update_streak(self):
        self.db.update_streak("Drink Water")
        self.db.update_streak("Drink Water", reset_streak=True)

    def test_delete_record(self):
        self.db.delete_record("Updated Test Habit")

    def test_display_habit_name(self):
        self.db.get_habit_names()

    def teardown_class(self):
        self.db.conn.close()  # Produces sqlite3 Error, but if I don't include this line then db doesn't delete
        os.remove("test.db")
