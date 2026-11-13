import heapq
from datetime import datetime

from enums.enums import TimeSlot, Destination
from models.models import RideRequest,Cab
import json
queues = {
    (d,t): []
    for d in Destination
    for t in TimeSlot
}
cabs: dict[int, Cab] = {}

def loadCabs():
    with open("data/cabs.json", "r") as c:
        data = json.load(c)
    for cab in data:


        students = [
            RideRequest(
                requestId=s["request-id"],
                name=s["name"],
                timeslot=TimeSlot[s["timeslot"].upper()],
                destination=Destination[s["destination"].upper()],
                timeOfRequest=s["timeOfRequest"],
                year=s["year"]
            )
            for s in cab.get("students", [])
        ]

        cabs.setdefault(cab["cab-id"],
            Cab(
                cabId=cab["cab-id"],
                name=cab["driver"],
                timeslot=TimeSlot[cab["time_slot"].upper()],
                destination=Destination[cab["destination"].upper()],
                seat=cab["seats"],
                students=students,
                departed=cab.get("departed", False)
            )
        )

def loadRequests():
    with open("data/requests.json", "r") as r:
        data = json.load(r)
    for req in data:
        reqobj = RideRequest(
                    requestId=req["request-id"],
                    name=req["name"],
                    timeslot=TimeSlot[req["timeslot"].upper()],
                    destination=Destination[req["destination"].upper()],
                    timeOfRequest=req["timeOfRequest"],
                    year=req["year"]
                )
        heapq.heappush(queues[reqobj.destination, reqobj.timeslot], (-reqobj.year, reqobj.timeOfRequest, reqobj.requestId, reqobj))

def viewQueue():
    for d in Destination:
        for t in TimeSlot:
            print("\nDestination: ", d.value)
            print("Timeslot: ", t.value)
            print("Current Queue:")
            print("RequestID Name Year Time of request")

            for priority, request_time, request_id, req in sorted(queues[d, t]):
                print(
                    req.requestId,
                    req.name,
                    req.year,
                    datetime.fromtimestamp(req.timeOfRequest)
                )
def viewCabs():
    print("CabID Name Timeslot Destination Seats CurrentStatus")
    for i in cabs.values():
        if i.departed:
            print(i.cabId,
                  i.name,
                  i.timeslot.value,
                  i.destination.value,
                  i.seat,
                  "DEPARTED")
            print("Students in cab")
            print("RequestID Name Year")
            for j in i.students:
                print(j.requestId, j.name, j.year)
        else:
            print(i.cabId,
                  i.name,
                  i.timeslot.value,
                  i.destination.value,
                  i.seat,
                  "WAITING")
def dispatchCab(cabid):
    cab = cabs.get(cabid)
    if cab is None:
        print("Invalid Cab Trip ID")
        return
    if cab.departed is True:
        print("Cab already departed")
        return
    destination = cab.destination
    timeslot = cab.timeslot
    empty = 0
    for i in range(cab.seat):
        try:
            priority, request_time, request_id, req = heapq.heappop(queues[destination, timeslot])
            cab.students.append(req)
        except IndexError:
            empty += 1
    if empty > 0:
        print(f"Cab {cabid} matched with {len(cab.students)} students with {empty} empty seats")
    else:
        print(f"Cab {cabid} matched with {len(cab.students)} students")
    cab.departed = True
def main():
    loadCabs()
    loadRequests()
    while True:
        print("\n===Student Cab Management===")
        print("1. Request a ride")
        print("2. View cabs and waiting students")
        print("3. Find matches")
        print("4. Dispatch a cab")
        print("5. Quit")
        choice = input("Choose action (1-5):-").strip()

        if choice == "1":
            print("2")
        elif choice == "2":
            choice = input("1. See available cabs\n2. See queue:-").strip()
            if choice == "1":
                viewCabs()
            elif choice == "2":
                viewQueue()
            else:
                print("Please enter 1 or 2")

        elif choice == "3":
            print("2")
        elif choice == "4":
            dispatchCab(int(input("Enter Trip ID")))
        elif choice == "5":
            print("Program exiting")
            break
        else:
            print("Please enter a number from 1 to 5")


if __name__ == '__main__':
    main()
