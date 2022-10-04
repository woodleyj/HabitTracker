from rich.table import Table

""" 
Functions to create tables using the Rich library.  Used to output a table in the terminal.

    title:  String
    columns: List of strings for the column headers
    rows: This should be a list of tuples, which is the output from the sqlite3 query
"""


def create_table(title: str = "Habits", columns: list = None, rows: list = None):
    table = Table(title=title)
    if columns is None:
        columns = ["Habit Name", "Description", "Interval", "Created Date", "Streak Count", "Max Streak",
                   "\N{heavy check mark}"]
    if rows is None:
        rows = ["None"]

    # Adding the columns and rows to the table
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row, style='bright_green')

    return table


def create_history_table(title: str = "Task History", columns: list = None, rows: list = None):
    table = Table(title=title)
    if columns is None:
        columns = ["Completed Date", "Completed Time", "Week", "Habit Name"]
    if rows is None:
        rows = ["None"]

    # Adding the columns and rows to the table
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row, style='bright_green')

    return table
