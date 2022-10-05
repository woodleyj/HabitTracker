import click
import inquirer
from os import path, remove
from rich import print
from datetime import datetime, timedelta
from resources.starter import starter_habits
from resources.habit import Habit
from resources.database import DBConn
from resources.table import create_table, create_history_table
from resources.menus import analyze_menu, create_delete_menu, create_habit_select_menu, interval_menu, modify_menu


def add_habit():
    """Prompts the user for input and adds the habit information provided to the database."""

    # Use the click prompts to get input from user
    name = click.prompt("Enter name of habit")
    desc = click.prompt("Enter description of habit (optional)", default="--", show_default=False)
    interval = inquirer.prompt(interval_menu)

    # Instantiate the habit object
    new_habit = Habit(name, desc, interval["selection"])

    # Create a connection to the db and add the new habit
    db = DBConn()
    message = db.add_record(new_habit.details)

    # Print the success/fail message to the user
    print(message)


def complete_task():
    """Prompts the user to select a task to complete, then updates the record in the database."""

    # Create a connection to the database and retrieve habit records to display to the user
    db = DBConn()
    habits = db.get_habit_names()
    if not habits:
        return print("No tasks to complete.  Maybe you should create some first :)")

    else:
        choices = [item for sublist in habits for item in sublist]
        choices.append("CANCEL")
        habit_select_menu = create_habit_select_menu(choices, message="Which task do you want to complete?")

        habit_name = inquirer.prompt(habit_select_menu)
        habit_name = habit_name["selection"]

        if habit_name == "CANCEL":
            return "Action Canceled."

        print(db.complete_task(habit_name=habit_name))


def delete_habit():
    """Prompts the user to select an existing habit and then deletes the habit information from the database."""

    # Create a connection to the db and retrieve the habit records
    db = DBConn()
    habits = db.get_habit_names()
    if not habits:
        return print("No Habits to delete.  Maybe you should create some first :)")

    else:
        # Show list of habit names to user and allow user to select
        choices = [item for sublist in habits for item in sublist]  # Just rearranging the output from the db to a list
        choices.append("CANCEL")
        delete_menu = create_delete_menu(choices)
        habit_name = inquirer.prompt(delete_menu)
        habit_name = habit_name["selection"]

        if habit_name == "CANCEL":
            return
        else:
            if click.confirm(f"Are you sure you want to delete '{habit_name}'?"):
                db.delete_record(habit_name)
                print(f"Habit '{habit_name}' deleted.")


def show_history():
    """Shows the history of all previously completed tasks."""

    # Create connection to the database and allow user to select which habit to which they want to see the history
    db = DBConn()
    habits = db.get_habit_names()
    if not habits:
        return print("No tasks to complete.  Maybe you should create some first :)")

    else:
        choices = [item for sublist in habits for item in sublist]
        choices.append("CANCEL")
        choices = ["ALL"] + choices
        habit_select_menu = create_habit_select_menu(choices, message="Which habit's history would you like to see?")

        habit_name = inquirer.prompt(habit_select_menu)
        habit_name = habit_name["selection"]

        if habit_name == "CANCEL":
            return "Action Canceled."
        elif habit_name == "ALL":
            history = db.get_all(table_name="tracker")
        else:
            history = db.get_all(table_name="tracker", habit_name=habit_name)

    # Arrange the information in a nice table to output to the user
    table = create_history_table(rows=history)
    print(table)


def show_interval(interval: str):
    """Retrieves only habits with a specified interval and outputs to the terminal."""

    # Create connection to the database and retrieve habits matching specified interval
    db = DBConn()
    habits = db.get_interval_habits(interval)

    if not habits:
        return "No habits to display"

    # Check the task streak
    habits = check_task_streak(habits)
    # Create a nice table to output to the user
    table = create_table(rows=habits)
    return table


def analyze_habits():
    """
    Show the Analyze Menu and allow the user to select further options for analysis.

    Show Daily - retrieve only the habits with Daily set as the interval.
    Show Weekly - retrieve only the habits with Weekly set as the interval.
    Longest Streak Overall - retrieve the habit with the longest streak.
    Longest Streak (selected task) - prompt user to select a habit, then show the streak information for that habit.
    """

    # Create a connection to the database
    db = DBConn()
    # Show Analyze menu to the user
    answer = inquirer.prompt(analyze_menu)

    if answer["selection"] == "Show Daily":
        table = show_interval("Daily")
        print(table)

    elif answer["selection"] == "Show Weekly":
        table = show_interval("Weekly")
        print(table)

    elif answer["selection"] == "Longest Streak Overall":
        longest = db.get_longest_streak()

        print(f"Your longest streak is {longest[5]}, for habit: '{longest[0]}', which should be completed "
              f"{longest[2].upper()}.")
        print(f"You started this habit on {longest[3]} and the current streak is {longest[4]}.")

    elif answer["selection"] == "Longest Streak (select habit)":
        tasks = db.get_habit_names()
        if not tasks:
            print("No habits to display.  Please create some first.")
            return

        choices = [t for task in tasks for t in task]
        choices.append("CANCEL")

        # Show user selection of habits to choose from
        habit_select_menu = create_habit_select_menu(choices)
        habit_selection = inquirer.prompt(habit_select_menu)
        habit_selection = habit_selection["selection"]

        if habit_selection == "CANCEL":
            print("Action canceled.")
            return

        longest = db.get_longest_streak(habit_selection)
        print(f"'{longest[0]}' -- {longest[2].upper()}: The longest streak for this habit is {longest[5]}.")
        print(f"You started this habit on {longest[3]} and the current streak is {longest[4]}.")

    else:
        return "Invalid Selection, try again."


def modify_habits():
    """Allows the user to modify different attributes of the currently tracked habits in the database."""

    # Create connection to the database and show habits to user
    db = DBConn()
    tasks = db.get_habit_names()
    if not tasks:
        print("No habits to display.  Please create some first.")
        return

    choices = [t for task in tasks for t in task]
    choices.append("CANCEL")

    # Show user selection of habits to choose from
    habit_select_menu = create_habit_select_menu(choices)
    habit_selection = inquirer.prompt(habit_select_menu)
    habit_selection = habit_selection["selection"]

    if habit_selection == "CANCEL":
        return "Action canceled."

    # Prompt user for type of modification
    answer = inquirer.prompt(modify_menu)

    if answer["selection"] == "Change Name":
        new_value = click.prompt("Enter new name for habit")
        if click.confirm(f"Update name of habit '{habit_selection}' to '{new_value}'?  "
                         f"WARNING: Streak will be lost, it will still be attached to the old name."):
            msg = db.update_record(habit_selection, "name", new_value)
            return msg
        else:
            return
    if answer["selection"] == "Change Description":
        new_value = click.prompt("Enter new description for habit")
        if click.confirm(f"Update description of habit '{habit_selection}' to '{new_value}'"):
            msg = db.update_record(habit_selection, "description", new_value)
            return msg
        else:
            return

    if answer["selection"] == "Change Interval":
        new_value = inquirer.prompt(interval_menu)
        new_value = new_value["selection"]
        if click.confirm(f"Update interval of habit '{habit_selection}' to '{new_value}'"):
            msg = db.update_record(habit_selection, "interval", new_value)
            return msg
        else:
            return

    if answer["selection"] == "CANCEL":
        return "Action canceled."


def check_task_streak(tasks: list = None):
    """
    Checks the streak for all the tasks (default) or a list of tasks (if specified) and updates accordingly.

    :param tasks: a list of tasks to check (optional)
    :return: list of tasks from the database
    """

    # Create connection to the database
    db = DBConn()
    if tasks is None:
        tasks = db.get_all()
    if not tasks:
        print("No habits to display.  Please create some first.")
        return

    # Set date information, so we can check if task was completed recently and if streak is still going
    today = str(datetime.today().date())
    yesterday = str(datetime.today().date() - timedelta(days=1))
    this_week = datetime.today().isocalendar()[1]
    last_week = this_week - 1

    # Fetch streak and task completion information and add it to list to display in table
    for row in tasks:

        # Row[0] represents the habit name
        records = db.get_history(row[0])
        # Check interval/periodicity - row[2] represents interval
        if row[2] == "Daily":
            if today in records:
                task_completion_status = "\N{heavy check mark} "
                completed_today = True
            else:
                task_completion_status = "\N{heavy multiplication x} "
                completed_today = False

            row.append(task_completion_status)

            # Check if Streak is maintained if habit currently has a streak
            # row[4] represents the Streak Count column
            if not row[4] == "0" and not completed_today:  # If it has a streak and not completed today
                if yesterday not in records:  # Check the records for yesterday's date and if not, reset streak
                    row[4] = "0"
                    db.update_streak(row[0], reset_streak=True)  # row[0] is habit name

        elif row[2] == "Weekly":
            if str(this_week) in records:
                task_completion_status = "\N{heavy check mark} "
                completed_this_week = True
            else:
                task_completion_status = "\N{heavy multiplication x} "
                completed_this_week = False

            row.append(task_completion_status)

            # Check if Streak is maintained if habit currently has a streak
            # row[4] represents the Streak Count column
            if not row[4] == "0" and not completed_this_week:  # If it has a streak and not completed this week
                if str(last_week) not in records:  # Check the records for last week's number and if not, reset streak
                    row[4] = "0"
                    db.update_streak(row[0], reset_streak=True)  # row[0] is habit name

    return tasks


def show_today():
    """Show all the currently tracked habits in a table format."""

    # Checking if streak is maintained
    tasks = check_task_streak()
    # Create a nice table to output to the user
    table = create_table(rows=tasks)
    print(table)


def reset():
    """Reset the app by deleting the database.  ***WARNING:  ALL DATA WILL BE LOST*** """
    remove("main.db")


@click.group()
def cli():
    """This little command-line app can be used to help you track your habits.  You can add, complete, and modify your
    habits, as well as see the history and your longest streaks.  Try using the interactive argument to get started."""
    pass


@cli.command("interactive")
def interactive_menu():
    """Interactive version of the CLI.  The app runs in a loop until you decide to exit by selecting the EXIT
    command from the menus.  Here you can see the different options within this application and navigate through
    them as much as you wish without having to call the main application with an argument like a traditional CLI.

    Use the arrow keys to change the selection and press ENTER to confirm selection."""
    main_menu = [
        inquirer.List(
            "selection",
            message="What would you like to do?",
            choices=["Add Habit", "Complete Task", "Delete Habit", "Analyze Habits",
                     "Modify Habits", "Show Today", "Exit App"],
        ),
    ]

    while True:
        sleep_time = 1.5
        print("Welcome to the Habit Tracker!")
        answer = inquirer.prompt(main_menu)

        if answer["selection"] == "Add Habit":
            add_habit()

        elif answer["selection"] == "Complete Task":
            complete_task()

        elif answer["selection"] == "Delete Habit":
            delete_habit()

        elif answer["selection"] == "Analyze Habits":
            analyze_habits()

        elif answer["selection"] == "Modify Habits":
            modify_habits()

        elif answer["selection"] == "Show Today":
            show_today()

        elif answer["selection"] == "Exit App":
            break

        click.prompt("Press Enter to continue", default="", show_default=False, prompt_suffix="...")


@cli.command("add-habit")
def add_habit_command():
    """Add a habit to your habit list."""
    add_habit()


@cli.command("delete-habit")
def delete_habit_command():
    """Delete a habit from your habit list."""
    delete_habit()


@cli.command("show-history")
def show_history_command():
    """Show the history of your habits."""
    show_history()


@cli.command("show-today")
def show_today_command():
    """Shows your current habits list."""
    show_today()


@cli.command("complete-task")
def complete_task_command():
    """Complete a task for a selected habit."""
    complete_task()


@cli.command("analyze-habits")
def analyze_habits_command():
    """Show all Daily, Weekly, or streak info for your habits."""
    analyze_habits()


@cli.command("modify-habits")
def modify_habits_command():
    """Modify the name, description, or interval of a habit."""
    modify_habits()


@cli.command("reset")
def reset_command():
    """Reset the app by deleting the database.  ***WARNING:  ALL DATA WILL BE LOST*** """
    reset()


if __name__ == '__main__':
    if not path.exists("main.db"):
        starter_habits()
    cli()
