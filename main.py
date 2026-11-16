import heapq
from datetime import datetime

from enums.enums import TimeSlot, Destination, getTimeSlot, getDestination
from models.models import RideRequest,Cab
import json
queues = {
    (d,t): []
    for d in Destination
    for t in TimeSlot
}
requestMap = {}
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
    global requests

    for cab in cabs.values():
        for student in cab.students:
            requests = max(requests, student.requestId)

def loadRequests():
    global requests
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
        requestMap[reqobj.requestId] = (reqobj.destination, reqobj.timeslot)
        if requests < reqobj.requestId:
            requests  = reqobj.requestId

def saveCabs():
    data = []
    for cab in cabs.values():
        cab_data = {
            "cab-id": cab.cabId,
            "driver": cab.name,
            "time_slot": cab.timeslot.value,
            "destination": cab.destination.value,
            "seats": cab.seat,
            "departed": cab.departed,
            "students": []
        }

        for s in cab.students:
            cab_data["students"].append({
                "request-id": s.requestId,
                "name": s.name,
                "timeslot": s.timeslot.value,
                "destination": s.destination.value,
                "timeOfRequest": s.timeOfRequest,
                "year": s.year
            })

        data.append(cab_data)
    with open("data/cabs.json", "w") as c:
        json.dump(data, c, indent=4)

def saveRequests():
    data = []

    for queue in queues.values():
        for req in queue:
            r = req[3]

            data.append({
                "request-id": r.requestId,
                "name": r.name,
                "timeslot": r.timeslot.value,
                "destination": r.destination.value,
                "timeOfRequest": r.timeOfRequest,
                "year": r.year
            })

    with open("data/requests.json", "w") as c:
        json.dump(data, c, indent=4)

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
                  str(len(i.students)) + "/" + str(i.seat),
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
                  "0/" + str(i.seat),
                  "WAITING")

def dispatchCabbyID(cabid):
    cab = cabs.get(cabid)
    if cab is None:
        print("Invalid Cab Trip ID")
        return
    if cab.departed is True:
        print("Cab has already left.")
        return
    destination = cab.destination
    timeslot = cab.timeslot
    empty = 0
    for i in range(cab.seat):
        try:
            priority, request_time, request_id, req = heapq.heappop(queues[destination, timeslot])
            requestMap.pop(req.requestId, None)
            cab.students.append(req)
        except IndexError:
            empty += 1
    if empty == cab.seat:
        print(f"No students waiting for {destination.value}, {timeslot.value}. Cab not sent.")
        return
    if empty > 0:
        print(f"Cab {cabid} matched with {len(cab.students)} students with {empty} empty seats")
    else:
        print(f"Cab {cabid} matched with {len(cab.students)} students")
    cab.departed = True
    try:
        saveCabs()
        saveRequests()
    except FileNotFoundError:
        print("JSON file not found!")

    except PermissionError:
        print("Permission denied while saving the file!")

    except json.JSONDecodeError:
        print("Invalid JSON format!")

    except TypeError:
        print("Object is not JSON serializable!")

    except OSError as e:
        print("File operation error:", e)

    except Exception as e:
        print("Unexpected error:", e)

def findCabs(destination, timeslot):
    for i in cabs.values():
        if not i.departed and i.destination == destination and i.timeslot == timeslot:
            print(i.cabId,
                  i.name,
                  i.timeslot.value,
                  i.destination.value,
                  i.seat,
                  "Waiting")

def findMatch(reqid):
    request = requestMap.get(reqid)
    if request is None:
        print(f"No waiting request with ID {reqid} (it may have already left in a cab).")
        return
    destination, timeslot = request
    currentavailableseats = 0
    availableCabs = {}
    for i in cabs.values():
        if not i.departed:
            if i.timeslot == timeslot and i.destination == destination:
                currentavailableseats += i.seat
                availableCabs.setdefault(currentavailableseats, i)
    if currentavailableseats > 0:
        for position, i in enumerate(sorted(queues[destination, timeslot])):
            if i[2] == reqid:
                print("Current Position in queue: ", position+1)
                print("Current Available seats", currentavailableseats)
                if currentavailableseats < position+1:
                    print("No matches found currently")
                else:
                    for y in availableCabs.keys():
                        if y >= position+1:
                            cab = availableCabs.get(y)
                            print("Cab Details:")
                            print("Cab ID: ", cab.cabId)
                            print("Driver Name: ", cab.name)
                            break
    else:
        print("No cabs found currently")

def addrequest():
    global requests
    name = input("Enter Name: ")
    if name.strip() == "":
        print("Name can't be empty.")
        return
    try:
        year = int(input("Enter Year: "))
        if year > 5 or year < 1:
            print("Year must be between 1 and 5.")
            return
        timeslot_code = int(
            input("Enter TimeSlot Code (Morning(1), Afternoon(2), Evening(3), Night(4)): ")
        )
        if timeslot_code > 4 or timeslot_code < 1:
            print("Time slot must be 1–4.")
            return
        destination_code = int(
            input("Enter Destination Code (Delhi(1), Jaipur(2)): ")
        )
        if destination_code > 2 or destination_code < 1:
            print("Invalid Destination Code!")
            return
    except ValueError:
        print("Please enter a number.")
        return

    timeslot = getTimeSlot(timeslot_code)
    destination = getDestination(destination_code)


    if timeslot is None:
        print("Invalid Timeslot!")
        return

    if destination is None:
        print("Invalid Destination!")
        return

    available = checkAvailableCabs(destination, timeslot)

    if not available:
        print("\nNo open cabs currently available for this trip.")
        print("Your request will be added to the waiting queue.")

    requests += 1

    request = RideRequest(
        requestId=requests,
        name=name.strip(),
        timeslot=timeslot,
        destination=destination,
        timeOfRequest=int(datetime.now().timestamp()),
        year=year
    )
    heapq.heappush(queues[request.destination, request.timeslot],
                   (-request.year, request.timeOfRequest, request.requestId, request))
    requestMap[request.requestId] = (request.destination, request.timeslot)
    print("Request ID:", requests)
    try:
        saveCabs()
        saveRequests()
    except FileNotFoundError:
        print("JSON file not found!")

    except PermissionError:
        print("Permission denied while saving the file!")

    except json.JSONDecodeError:
        print("Invalid JSON format!")

    except TypeError:
        print("Object is not JSON serializable!")

    except OSError as e:
        print("File operation error:", e)

    except Exception as e:
        print("Unexpected error:", e)

def checkAvailableCabs(destination, timeslot):
    for cab in cabs.values():
        if (cab.destination == destination
                and cab.timeslot == timeslot
                and not cab.departed):
            return True
    return False

def main():
    try:
        try:
            loadCabs()
            loadRequests()

        except FileNotFoundError as e:
            print(f"Data file not found: {e.filename}")
            print("Please make sure data/cabs.json and data/requests.json exist.")

        except json.JSONDecodeError as e:
            print(f"Invalid JSON file: {e}")

        except PermissionError as e:
            print(f"Permission denied: {e}")

        except (KeyError, ValueError, TypeError, AttributeError) as e:
            print(f"Invalid data in JSON file: {e}")

        except OSError as e:
            print(f"File operation error: {e}")
        while True:
            print("\n===Student Cab Management===")
            print("1. Request a ride")
            print("2. View cabs and waiting students")
            print("3. Find matches")
            print("4. Dispatch a cab")
            print("5. Quit")
            choice = input("Choose action (1-5): ").strip()

            if choice == "1":
                addrequest()
            elif choice == "2":
                choice = input("1. See available cabs\n2. See queue\nChoose action (1 or 2): ").strip()
                if choice == "1":
                    viewCabs() #add3/4 seats issue
                elif choice == "2":
                    viewQueue()
                else:
                    print("Please enter 1 or 2")

            elif choice == "3":
                try:
                    findMatch(int(input("Enter Request ID: ")))
                except ValueError:
                    print("Request ID must be a number.")
            elif choice == "4":
                try:
                    timeslot_code = int(
                        input("Enter TimeSlot Code (Morning(1), Afternoon(2), Evening(3), Night(4)): ")
                    )
                    if timeslot_code > 4 or timeslot_code < 1:
                        print("Time slot must be 1–4.")
                        continue
                    destination_code = int(
                        input("Enter Destination Code (Delhi(1), Jaipur(2)): ")
                    )
                    if destination_code > 2 or destination_code < 1:
                        print("Invalid Destination Code!")
                        continue

                    timeslot = getTimeSlot(timeslot_code)
                    destination = getDestination(destination_code)
                    findCabs(destination, timeslot)
                    dispatchCabbyID(int(input("Enter Trip ID: ")))
                except ValueError:
                    print("Please enter a number.")
            elif choice == "5":
                print("Program exiting")
                break
            else:
                print("Please enter a number from 1 to 5")

    except (KeyboardInterrupt, EOFError):
        print("Program exiting")


if __name__ == '__main__':
    requests = 0
    main()
