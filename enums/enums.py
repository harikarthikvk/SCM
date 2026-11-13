from enum import Enum

cities = ["Delhi", "Jaipur"]

class TimeSlot(Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    NIGHT = "Night"

Destination = Enum("Destination", {city.upper(): city for city in cities})
