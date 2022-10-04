from datetime import datetime


class Habit:
    def __init__(self, name: str, desc: str, interval: str):
        self.name = name
        self.desc = desc
        self.interval = interval
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.streak_count = 0
        self.max_streak = 0

        self.details = [self.name, self.desc, self.interval, self.created_date, self.streak_count, self.max_streak]


