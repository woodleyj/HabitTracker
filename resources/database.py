import sqlite3
from datetime import datetime, timedelta, time


class DBConn:
    """
    This is the class for the Database Connection object that includes functions for all the CRUD operations for the
    database.
    """

    def __init__(self, name="main.db"):
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS habits (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    interval TEXT,
                    created_date TEXT,
                    streak_count INTEGER,
                    max_streak INTEGER)""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tracker (
                            completed_date TEXT,
                            completed_time TEXT,
                            completed_week TEXT,
                            habit_name TEXT,
                            FOREIGN KEY (habit_name) REFERENCES habits(name))""")

        self.conn.commit()

    def __del__(self):
        """Method that is automatically called to close the database connection."""

        self.cursor.close()
        self.conn.close()

    def add_record(self, habit_details: list):
        """
        Add record to the database/habits table.

        :param habit_details: list containing the habit information; expecting a list of 6 items
        :return: success/fail message of the database operation
        """

        # Unpack the list of habit details into their own variables
        habit_name, habit_desc, interval, created_date, streak_count, max_streak = habit_details

        try:
            self.cursor.execute(
                "INSERT INTO habits (name, description, interval, created_date, streak_count, max_streak) "
                "VALUES (:name, :desc, :interval, :created_date, :streak_count, :max_streak)",
                {'name': habit_name,
                 'desc': habit_desc,
                 'interval': interval,
                 'created_date': created_date,
                 'streak_count': streak_count,
                 'max_streak': max_streak})
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            return e, "ERROR: Habit already exists with that name!  Try again with a new name."

        return f"Habit '{habit_name}' added successfully."

    def add_history(self, habit_name: str, completed_date: str, completed_time: str, completed_week: str):
        self.cursor.execute("INSERT INTO tracker "
                            "VALUES (:completed_date, :completed_time, :completed_week, :habit_name)",
                            {'completed_date': completed_date,
                             'completed_time': completed_time,
                             'completed_week': completed_week,
                             'habit_name': habit_name})

    def check_streak(self, habit_name: str, completed_date: str, completed_week: str):
        """
        Check the streak of a habit and update if necessary.

        :param habit_name: name of the habit
        :return: None
        """

        # Get interval of selected habit
        habit_interval = self.get_interval(habit_name)

        # Check if task was already completed today/this week
        history = self.get_history(habit_name)

        if habit_interval == "Daily":
            # Only update streak count if task has not already been completed today
            if completed_date not in history:
                print("Updating streak count...")
                self.update_streak(habit_name)
        elif habit_interval == "Weekly":
            # Only update streak count if task has not already been completed this week
            if completed_week not in history:
                print("Updating streak count...")
                self.update_streak(habit_name)

        return

    def complete_task(self, habit_name: str):
        """
        Mark a task as complete in the database.

        :param habit_name: name of the habit
        :return: success/error message from the database operation
        """

        # Get current day and week
        date = datetime.now()
        completed_date = date.strftime("%Y-%m-%d")
        completed_time = date.strftime("%H:%M")
        completed_week = str(date.isocalendar().week)

        # Check the streak
        self.check_streak(habit_name, completed_date, completed_week)

        # Add history of completion to the database
        try:
            self.add_history(habit_name, completed_date, completed_time, completed_week)

        except Exception as e:
            return e

        self.conn.commit()

        return f"{self.cursor.rowcount} row(s) inserted successfully."

    def delete_record(self, habit_name: str):
        """
        Delete habit from the database.

        :param habit_name: name of habit
        """

        self.cursor.execute("DELETE from habits where name=:habit_name", {'habit_name': habit_name})
        self.conn.commit()

    def get_all(self, table_name: str = "habits", habit_name: str = None):
        """
        Retrieve all habit records from the specified table.

        :param table_name: name of the table from which to retrieve records
        :param habit_name: name of the habit (optional)
        :return: nested list of habits/habit information
        """

        if habit_name is None:
            if table_name == "habits":
                self.cursor.execute("SELECT * FROM habits")
            elif table_name == "tracker":
                self.cursor.execute("SELECT * FROM tracker ORDER BY completed_date ASC")

        elif habit_name is not None:
            # If habit name was specified then only retrieve those records from specified table
            if table_name == "habits":
                self.cursor.execute("SELECT * FROM habits WHERE name=:habit_name", {'habit_name': habit_name})
            elif table_name == "tracker":
                self.cursor.execute("SELECT * FROM tracker WHERE habit_name=:habit_name ORDER BY completed_date ASC",
                                    {'habit_name': habit_name})

        records = self._convert_to_lists(self.cursor.fetchall())

        return records

    def get_habit_names(self):
        """
        Simple function to retrieve habit names from the habits table.

        :return: raw output of habit names from database
        """
        self.cursor.execute("SELECT name FROM habits")
        return self.cursor.fetchall()

    def get_history(self, habit_name: str):
        """
        Retrieve the history of a specific habit.

        :param habit_name: name of the habit
        :return: list of habit information
        """

        self.cursor.execute("SELECT completed_date, completed_week FROM tracker WHERE habit_name = :habit_name",
                            {'habit_name': habit_name})
        return self._convert_to_lists(self.cursor.fetchall(), nested_list=False)

    def get_interval(self, habit_name: str):
        """
        Basic function to retrieve the interval for a specified habit.

        :param habit_name: name of the habit
        :return: the interval of the specified habit
        """

        self.cursor.execute("SELECT interval FROM habits WHERE name = :habit_name", {'habit_name': habit_name})
        return self._convert_to_lists(self.cursor.fetchall(), nested_list=False)[0]

    def get_interval_habits(self, interval: str):
        """
        Retrieve only habits that match the specified interval.

        :param interval: interval type, Daily or Weekly
        :return: nested list of habits matching the specified interval
        """

        self.cursor.execute("SELECT * FROM habits WHERE interval=:interval", {'interval': interval})
        return self._convert_to_lists(self.cursor.fetchall())

    def get_longest_streak(self, habit_name: str = None):
        """
        Retrieve the habit with the longest streak (default) or the streak information for a habit if specified.

        :param habit_name: name of the habit
        :return: list of habit/streak information
        """
        if habit_name is None:
            self.cursor.execute("SELECT *, max(max_streak) FROM habits")

        else:
            self.cursor.execute("SELECT * FROM habits WHERE name = :habit_name", {'habit_name': habit_name})

        return self._convert_to_lists(self.cursor.fetchall(), nested_list=False)

    def update_record(self, habit_name: str, attr_to_update: str, update_value: str):
        """
        Update a specific record in the database.

        :param habit_name: name of habit
        :param attr_to_update: attribute of habit to update; 'name', 'description', 'interval' are supported options.
        :param update_value: new value to set on attribute
        :return: success/fail message from database operation
        """

        if attr_to_update == "name":
            self.cursor.execute("UPDATE habits SET name= :update_value WHERE name =:habit_name",
                                {'update_value': update_value, 'habit_name': habit_name})

        if attr_to_update == "description":
            self.cursor.execute("UPDATE habits SET description= :update_value WHERE name =:habit_name",
                                {'update_value': update_value, 'habit_name': habit_name})

        if attr_to_update == "interval":
            self.cursor.execute("UPDATE habits SET interval= :update_value WHERE name =:habit_name",
                                {'update_value': update_value, 'habit_name': habit_name})

        self.conn.commit()
        if self.cursor.rowcount == 0:
            return "No records updated.  Check for programming errors in SQL query."
        else:
            return f"Updated {self.cursor.rowcount} record(s) successfully."

    def update_streak(self, habit_name: str, reset_streak: bool = False):
        """
        Update the streak for a specified habit.  Can be used to add to streak or reset streak back to zero.

        :param habit_name: name of habit
        :param reset_streak: boolean value; set to True to reset the streak to zero
        :return: None
        """

        if reset_streak:
            self.cursor.execute("UPDATE habits SET streak_count = 0 WHERE name =:habit_name",
                                {'habit_name': habit_name})
            self.conn.commit()
            return f"Streak Count reset for habit: {habit_name} !"

        self.cursor.execute("SELECT streak_count, max_streak FROM habits WHERE name = :habit_name",
                            {'habit_name': habit_name})
        streak_list = self._convert_to_lists(self.cursor.fetchall(), nested_list=False)
        streak_count = streak_list[0] + 1
        max_streak = streak_count if streak_count > streak_list[1] else streak_list[1]
        self.cursor.execute("UPDATE habits SET streak_count = :streak_count, max_streak = :max_streak "
                            "WHERE name =:habit_name", {"streak_count": streak_count,
                                                        "max_streak": max_streak,
                                                        "habit_name": habit_name})
        self.conn.commit()
        return

    @staticmethod
    def _convert_to_lists(tuple_list: list, nested_list: bool = True):
        """
        Static method used to convert the database output to an easier-to-use list format.

        :param tuple_list: list of tuples (output from database fetch* operations)
        :param nested_list: boolean set to True by default; set to False if a plain list is needed instead
        :return: nested list(default) or list
        """

        if nested_list:
            return [[str(item) for item in tup] for tup in tuple_list]
        else:
            return [item for tup in tuple_list for item in tup]
