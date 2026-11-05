from dataclasses import dataclass, field
from enums.enums import TimeSlot, Destination

@dataclass
class RideRequest:
    name: str
    timeslot: TimeSlot
    destination: Destination
    timeOfRequest: float
    year: int
    def __post_init__(self):
        if self.year > 5:
            raise ValueError("Student year cannot be more than 5 years.")
        if self.timeslot not in TimeSlot:
            raise ValueError("Timeslot doesnt exist")
        if self.destination not in Destination:
            raise ValueError("Destination city doesnt exist")

@dataclass
class Cab:
    name: str
    timeslot: TimeSlot
    destination: Destination
    seat: int
    students: list[RideRequest] = field(default_factory=list)
    status: bool = False
