

class Habit:
    def __init__(self, name: str, description: str, interval: str):
        self.name = name
        self.description = description
        self.interval = interval

    def __repr__(self):
        return(f'{self.name} | {self.description} | {self.interval}')