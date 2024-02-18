from dataclasses import dataclass

@dataclass
class Event:
    name: str
    start: str
    end: str
    
    def __str__(self):
        return f"""Event: {self.name}\nStarting time: {self.start}"""