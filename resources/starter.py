from datetime import datetime, timedelta
from resources.database import DBConn
from resources.habit import Habit


def starter_habits(db_name: str = None):
    """Set up the first 5 starter habits for the user"""

    # Open connection to database
    if db_name is not None:
        db = DBConn(db_name)
    else:
        db = DBConn()

    habits = ["Drink Water", "Read", "Exercise", "Meditate", "Walk in Nature"]
    descriptions = ["One Liter", "One Chapter", "Thirty Minutes", "Twenty Minutes", "One Hour"]
    intervals = ["Daily", "Daily", "Daily", "Daily", "Weekly"]

    print("Setting up starter habits...\n")

    # Loop through and create the 5 starter habits and write to database
    for i in range(len(habits)):
        new_habit = Habit(habits[i], descriptions[i], intervals[i])
        message = db.add_record(new_habit.details)
        print(message)

        # Add 4 weeks of history
        if intervals[i] == "Daily":
            print(f"Adding history for {habits[i]} starter task...")
            for j in range(1, 29):
                date = datetime.today() - timedelta(days=j)
                completed_date = date.strftime("%Y-%m-%d")
                completed_time = date.strftime("%H:%M")
                completed_week = str(date.isocalendar().week)
                db.add_history(habits[i], completed_date, completed_time, completed_week)

        if intervals[i] == "Weekly":
            print(f"Adding history for {habits[i]} starter task...")
            for k in range(1, 5):
                date = datetime.today() - timedelta(weeks=k)
                completed_date = date.strftime("%Y-%m-%d")
                completed_time = date.strftime("%H:%M")
                completed_week = str(date.isocalendar().week)
                db.add_history(habits[i], completed_date, completed_time, completed_week)

    db.conn.commit()