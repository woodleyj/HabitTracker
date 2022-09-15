import inquirer

"""
All of the different menus that can be displayed in the habit tracker.
"""

analyze_menu = [
    inquirer.List(
        "selection",
        message="What would you like to do?",
        choices=["Show Daily", "Show Weekly", "Longest Streak Overall", "Longest Streak (select habit)"]
    ),
]

interval_menu = [
    inquirer.List(
        "selection",
        message="Which interval would you like this habit to be performed?",
        choices=["Daily", "Weekly"]
    ),
]

modify_menu = [
    inquirer.List(
        "selection",
        message="What would you like to do?",
        choices=["Change Name", "Change Description", "Change Interval"]
    ),
]


def create_delete_menu(choices: list):
    delete_menu = [
        inquirer.List(
            "selection",
            message="Which habit would you like to delete?",
            choices=choices
        ),
    ]
    return delete_menu


def create_habit_select_menu(choices: list, message: str = "Which habit would you like to change?"):
    habit_select_menu = [
        inquirer.List(
            "selection",
            message=message,
            choices=choices
        ),
    ]
    return habit_select_menu
