from dataclasses import dataclass, field
from enums.enums import TimeSlot, Destination

@dataclass
class RideRequest:
    requestId: int
    name: str
    timeslot: TimeSlot
    destination: Destination
    timeOfRequest: float
    year: int

@dataclass
class Cab:
    cabId: int
    name: str
    timeslot: TimeSlot
    destination: Destination
    seat: int
    students: list[RideRequest] = field(default_factory=list)
    departed: bool = False
