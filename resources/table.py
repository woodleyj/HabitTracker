from rich.table import Table

""" Function to create a table using the Rich library.  Used to output a table in the terminal.
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

    # Retrieving streak and task completion data then adding it to the list which will be displayed in the table
    # Get Streak Count
    # Get Max Streak
    # for sublist in rows:
    #     sublist.extend(['0', '0', '0'])
    # print(rows)
    # for i in range(len(rows)):
    #     if rows[i][-2] == "1":
    #         rows[i][-2] = "\N{heavy check mark} "
    #     else:
    #         rows[i][-2] = "\N{heavy multiplication x} "

    # Adding the columns and rows to the table
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row, style='bright_green')

    return table


def create_history_table(title: str = "Task History", columns: list = None, rows: list = None):
    table = Table(title=title)
    if columns is None:
        columns = ["Completed Date", "Week", "Habit Name"]
    if rows is None:
        rows = ["None"]

    # Adding the columns and rows to the table
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row, style='bright_green')

    return table
