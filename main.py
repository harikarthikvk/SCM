from enums.enums import TimeSlot, Destination
from models.models import RideRequest,Cab
import json
requestQueue: list[RideRequest] = []
cabQueue: list[Cab] = []

def loadCabs():
    cabQueue.clear()
    with open("cabs.json", "r") as c:
        data = json.load(c)
    for cab in data:
        if cab.get("status", False):
            continue

        students = [
            RideRequest(
                name=s["name"],
                timeslot=TimeSlot[s["timeslot"]],
                destination=Destination[s["destination"].upper()],
                timeOfRequest=s["timeOfRequest"],
                year=s["year"]
            )
            for s in cab.get("students", [])
        ]

        cabQueue.append(
            Cab(
                name=cab["driver"],
                timeslot=TimeSlot[cab["time_slot"].upper()],
                destination=Destination[cab["destination"].upper()],
                seat=cab["seats"],
                students=students,
                status=cab.get("status", False)
            )
        )

def loadRequests():
    requestQueue.clear()
    with open("requests.json", "r") as r:
        data = json.load(r)
    for req in data:
        requestQueue.append(
            RideRequest(
                name=req["name"],
                timeslot=TimeSlot[req["timeslot"]],
                destination=Destination[req["destination"].upper()],
                timeOfRequest=req["timeOfRequest"],
                year=req["year"]
            )
        )


if __name__ == '__main__':
    loadCabs()
    loadRequests()