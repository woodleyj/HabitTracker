import click
import inquirer
from rich import print
from datetime import datetime, timedelta
from resources.database import DBConn
from resources.table import create_table, create_history_table
from resources.menus import analyze_menu, create_delete_menu, create_habit_select_menu, interval_menu, modify_menu


def add_habit():
    name = click.prompt("Enter name of habit")
    desc = click.prompt("Enter description of habit (optional)", default="--", show_default=False)
    interval = inquirer.prompt(interval_menu)

    db = DBConn()
    message = db.add_record(name, desc, interval['selection'])
    click.echo(message)


def delete_habit():
    db = DBConn()
    habits = db.display_habit_names()
    if not habits:
        return click.echo("No Habits to delete.  Maybe you should create some first :)")

    else:
        choices = [item for sublist in habits for item in sublist]
        choices.append("CANCEL")
        delete_menu = create_delete_menu(choices)
        habit_name = inquirer.prompt(delete_menu)
        habit_name = habit_name["selection"]

        if habit_name == "CANCEL":
            return
        else:
            if click.confirm(f"Are you sure you want to delete '{habit_name}'?"):
                db.delete_record(habit_name)
                click.echo(f"Habit '{habit_name}' deleted.")


def complete_task():
    db = DBConn()
    # Show Tasks for today
    habits = db.display_habit_names()
    print(habits)
    if not habits:
        return click.echo("No tasks to complete.  Maybe you should create some first :)")

    else:
        choices = [item for sublist in habits for item in sublist]
        choices.append("CANCEL")
        habit_select_menu = create_habit_select_menu(choices, message="Which task do you want to complete?")

        habit_name = inquirer.prompt(habit_select_menu)
        habit_name = habit_name["selection"]

        if habit_name == "CANCEL":
            return "Action Canceled."

        return db.complete_task(habit_name=habit_name)


def display_history():
    db = DBConn()
    history = db.display_all(table_name="tracker")

    table = create_history_table(rows=history)
    return table


def show_interval(interval: str):
    db = DBConn()

    habits = db.display_interval_habits(interval)

    if not habits:
        return "No habits to display"

    habits = check_task_streak(habits)

    table = create_table(rows=habits)
    return table


def analyze_habits():
    db = DBConn()

    answer = inquirer.prompt(analyze_menu)

    if answer["selection"] == "Show Daily":
        table = show_interval("Daily")
        print(table)

    elif answer["selection"] == "Show Weekly":
        table = show_interval("Weekly")
        print(table)

    elif answer["selection"] == "Longest Streak Overall":
        return "COMING SOON"

    elif answer["selection"] == "Longest Streak (select habit)":
        return "COMING SOON"

    else:
        return "Invalid Selection, try again."


def modify_habits():
    db = DBConn()
    tasks = db.display_habit_names()
    if not tasks:
        click.echo("No habits to display.  Please create some first.")
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
    db = DBConn()
    if tasks is None:
        tasks = db.display_all()
    if not tasks:
        click.echo("No habits to display.  Please create some first.")
        return

    today = str(datetime.today().date())
    yesterday = str(datetime.today().date() - timedelta(days=1))
    this_week = datetime.today().isocalendar()[1]
    last_week = this_week - 1

    # Fetch streak and task completion information and add it to list to display in table
    for row in tasks:

        # Row[0] represents the habit name
        records = db.fetch_habit_history(row[0])
        # Check interval/periodicity
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
    db = DBConn()

    # Checking if streak is maintained
    tasks = check_task_streak()

    table = create_table(rows=tasks)
    print(table)


def exit_cleanup():
    return "Saving changes... Exit."


@click.group()
def cli():
    pass


@cli.command()
def interactive_menu():
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
        click.echo("Welcome to the Habit Tracker!")
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
            exit_cleanup()
            break

        click.prompt("Press Enter to continue", default="", show_default=False, prompt_suffix="...")


@cli.command("add-habit")
def add_habit_command():
    add_habit()


@cli.command("delete-habit")
def delete_habit_command():
    click.echo(delete_habit())


@cli.command("display-history")
def display_history_command():
    print(display_history())


@cli.command("show-today")
def show_today_command():
    print(show_today())


@cli.command("complete-task")
def complete_task_command():
    click.echo(complete_task())


@cli.command("analyze-habits")
def analyze_habits_command():
    click.echo(analyze_habits())


@cli.command("modify-habits")
def modify_habits_command():
    click.echo(modify_habits())


if __name__ == '__main__':
    cli()
