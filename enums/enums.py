from enum import Enum

cities = ["Delhi", "Jaipur"]

class TimeSlot(Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    NIGHT = "Night"

Destination = Enum("Destination", {city.upper(): city for city in cities})

def getTimeSlot(code):
    try:
        return list(TimeSlot)[code - 1]
    except (IndexError, TypeError):
        return None


def getDestination(code):
    try:
        return list(Destination)[code - 1]
    except (IndexError, TypeError):
        return None