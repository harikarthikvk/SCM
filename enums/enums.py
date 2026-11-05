from enum import Enum

cities = ["Delhi", "Jaipur"]

class TimeSlot(Enum):
    MORNING = "09:00-12:00"
    AFTERNOON = "12:00-16:00"
    EVENING = "16:00-20:00"
    NIGHT = "20:00-00:00"

Destination = Enum("Destination", {city.upper(): city for city in cities})
