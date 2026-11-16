# SCM: Student Cab Manager

A command-line cab pool matcher for the end-of-semester rush, built for the SUTT Back-End recruitment (Task 1).
Students submit ride requests to Delhi or Jaipur for a time slot. Requests wait in a seniority-ordered queue, and cabs are filled from that queue only when they are dispatched. Because of this, a senior who signs up late still gets a seat ahead of a junior who signed up early.

## Requirements

- Python 3.9 or newer (the code uses `dict[...]` / `list[...]` type hints)
- No external packages. Only the standard library is used (`heapq`, `json`, `datetime`, `dataclasses`, `enum`), so there is no `requirements.txt`.

## How to run

Run from the project root, because the data paths are relative:

```bash
git clone https://github.com/harikarthikvk/SCM.git
cd SCM
python3 main.py
```

## Project structure

```
SCM/
├── main.py                    # menu, loading/saving, queues, matching and dispatch
├── models/models.py           # RideRequest and Cab dataclasses
├── enums/enums.py             # TimeSlot and Destination enums + code-to-enum helpers
└── data/
    ├── cabs-initial.json      # sample cabs (clean starting data)
    ├── requests-initial.json  # sample waiting requests (clean starting data)
    ├── cabs.json              # current cab state (saved by the app)
    └── requests.json          # current waiting list (saved by the app)
```

To reset the app to the sample data, copy the `*-initial.json` files over `cabs.json` and `requests.json`.

## Using the app

```
===Student Cab Management===
1. Request a ride
2. View cabs and waiting students
3. Find matches
4. Dispatch a cab
5. Quit
```

| Option | What it does |
|---|---|
| 1. Request a ride | Asks for name, year (1–5), time slot and destination. The request joins the waiting queue for that trip and you get a request ID. If no open cab serves that trip, you are told, but the request still waits. |
| 2. View | Shows all cabs (seats taken / total, open or departed, and passengers of departed cabs), or the waiting queue for every trip in seniority order. |
| 3. Find matches | Enter a request ID to see your position in your trip's queue, the open seats for that trip, and which cab you would get if cabs left now. It is a preview only: nothing changes. |
| 4. Dispatch a cab | Pick a time slot and destination, see the open cabs for that trip, then choose one to send. It takes the most senior waiting students, up to its seat count. |
| 5. Quit | Exits. All changes are already saved (see [Saving state](#saving-state)). |

Codes used in prompts:

- **Time slot:** 1 Morning, 2 Afternoon, 3 Evening, 4 Night
- **Destination:** 1 Delhi, 2 Jaipur

Invalid input (an empty name, a year outside 1–5, an unknown code, or text where a number is expected) shows a short error and returns to the menu instead of crashing.

## Data file format

### Cabs (`data/cabs.json`)

A JSON list of cabs. Cabs are always processed in the order they appear in this file, so results are the same every run.

```json
[
  {
    "cab-id": 1,
    "driver": "Ramesh Kumar",
    "seats": 4,
    "destination": "Delhi",
    "time_slot": "Morning",
    "departed": false,
    "students": []
  }
]
```

| Field | Type | Notes |
|---|---|---|
| `cab-id` | int | Unique ID, used when dispatching |
| `driver` | string | Driver's name |
| `seats` | int | 1 to 4 |
| `destination` | string | `Delhi` or `Jaipur` (case-insensitive) |
| `time_slot` | string | `Morning`, `Afternoon`, `Evening` or `Night` (case-insensitive) |
| `departed` | bool | Optional, defaults to `false` |
| `students` | list | Optional. Passengers, filled in by the app when the cab is dispatched. Same fields as a request below. |

### Requests (`data/requests.json`)

A JSON list of waiting requests:

```json
[
  {
    "request-id": 1,
    "name": "Aarav",
    "timeslot": "Morning",
    "destination": "Delhi",
    "timeOfRequest": 1794558600,
    "year": 2
  }
]
```

`timeOfRequest` is a Unix timestamp in whole seconds. Together with `request-id`, it decides who is first among students of the same year. New request IDs continue from the highest ID found in either file, including students already in cabs, so IDs are never reused.

## Design

### Seniors first: one priority queue per trip

There is one heap for every (destination, time slot) pair, so 8 heaps. They are kept in a dict, so finding the right queue is O(1). The queue belongs to the trip, not to a cab, and a cab's passenger list is a normal list.

Each heap entry is a tuple:

```python
(-year, timeOfRequest, requestId, request)
```

- **`-year`:** `heapq` is a min-heap. Negating the year puts the most senior student (year 5 → -5) at the top, which turns it into a max-heap on year.
- **`timeOfRequest`:** among students of the same year, the earlier request comes first.
- **`requestId`:** a unique tie-breaker if two requests share a year and a timestamp, for example two requests within the same second.
- **`request`:** the `RideRequest` itself. Because `requestId` is unique, Python's tuple comparison always decides before reaching this element, so two `RideRequest` objects are never compared. That comparison would raise a `TypeError`.

### Find Matches works per request

Find Matches looks up one request instead of previewing every cab. To work out which cab a student would get, the app walks the open cabs for that trip in file order and keeps a running total of seats. The student gets the first cab where that total reaches their position in the queue. If their position is past the total, there is no seat for them yet.

### Open cabs are always empty

Students are only placed in a cab at the moment it is dispatched, and a dispatched cab is closed for good. So an open cab never has passengers, and dispatch can use its full seat count.

## Saving state

The app saves to `data/cabs.json` and `data/requests.json` after every change: adding a request and dispatching a cab. Quitting, closing the terminal or pressing Ctrl+C loses nothing, because everything is already on disk. There is no separate save on exit. A save at shutdown is the most likely save to be interrupted and the hardest to recover from, so it was removed.

**Why JSON and not pickle:**
- JSON is human-readable. Anyone can open the file and check who is waiting or in which cab, or fix a mistake by hand.
- It shows up as a readable diff in git.
- It isn't tied to Python or to the class definitions in this code.
- Loading a pickle file can run arbitrary code, so a tampered save file would be a security risk. Loading JSON only ever produces data.

**When a save fails** (for example, no permission to write): the app prints the error and keeps running, and the change is kept in memory. Every save writes the full state, so the next successful save also writes the change that failed.

**Keeping places in line after a restart:** each saved request stores its year, `timeOfRequest` and `request-id`. On startup, the heaps are rebuilt from these values, so every student is in exactly the same order as before. A 3rd year who asked before another 3rd year is still ahead of them. The order the requests were written in doesn't matter.

**When a data file is missing or broken:** the app catches the error (missing file, invalid JSON, a missing field, or an unknown city or time slot), prints which problem it found, and keeps running instead of crashing. To start completely fresh, copy the `*-initial.json` files over the current ones.

## Tricky situations

### 1. Half-empty cab

A cab can be sent off with fewer students than seats. It takes everyone waiting for its trip, up to its seat count, and the app reports how many seats were left empty. The cab is then marked as departed and can't take anyone else. If **nobody** is waiting for that trip, the cab is not sent and nothing changes, so the cab stays open for later requests.

### 2. No cabs left

If every cab for a trip has already left, or there are no cabs at all, a student can still submit a request. The app tells them that no open cab serves that trip right now, and adds them to the waiting queue anyway. Find Matches tells them there are no cabs for their trip. A request only leaves the queue when its student is placed in a dispatched cab. It is never dropped, and it is saved to disk, so it survives restarts too.

### 3. Same year

The heap orders entries by the full tuple `(-year, timeOfRequest, requestId, request)`. When two students have the same year, the first elements are equal, so the comparison moves on to `timeOfRequest` and the earlier request wins. If even the timestamps are equal, the unique `requestId` decides, so the comparison never reaches the `RideRequest` objects (see [Design](#seniors-first-one-priority-queue-per-trip)).

### 4. Lots of students (1,000 waiting)

Here *n* is the number of waiting requests, *k* the number of seats in a cab (at most 4) and *C* the number of cabs.

| Operation | Complexity | Why |
|---|---|---|
| Adding one request | O(log n) for the queue | `heapq.heappush` moves the new entry up the heap, which takes at most log n swaps. Picking the right heap is O(1), because the queues are a dict keyed by (destination, time slot). |
| Adding all 1,000 | O(n log n) | 1,000 pushes of O(log n) each. When loading from the file at startup, putting everything into a list and calling `heapq.heapify` once would bring this down to O(n). |
| Dispatching one cab (up to 4 students) | O(k log n), effectively O(log n) | Each of the k pops is O(log n), and k ≤ 4 is a constant. Finding the cab by ID is O(1) with a dict lookup. |
| Finding an open cab for a trip | O(C) | A linear scan over the cabs, in file order. C is small (a handful of cabs), so this is fine. A dict of open cabs per trip would make it O(1). |

**Cost of saving.** Saving after every change rewrites the whole state, which is O(n + C). That makes the save, not the heap, the slowest part of adding a request: in practice adding one request is O(n), and adding 1,000 one after another is O(n²) in total. For a campus-sized list this is still fast. It's the price of never losing data. Saving only what changed, or using a database such as SQLite, would remove it.

## Known limitations and possible improvements

- **Writes are not atomic.** If the app is killed during a save, the file can be left half-written. Writing to a temp file and swapping it in with `os.replace` would fix this.
- **Cabs and requests are saved to two separate files.** A crash between the two writes could leave them out of sync. One combined state file would avoid this.
- **A partly broken data file isn't fully recovered.** The app reports the problem and keeps running with whatever loaded, and the next save writes that state back. Automatically falling back to the `*-initial.json` files (and keeping a backup of the broken file) would be safer.
- **The cab is chosen by hand when dispatching.** The app could pick the first open cab for the chosen trip automatically.
- **No automated tests yet.**

---

*A note on how this README was made:* I wrote this README with AI (Claude) by giving it the entire repository, then reviewed it against the code. The app itself is my own work. I believe that not using AI for tasks like writing documentation is wasted potential: it turns a working codebase into clear docs quickly, which leaves more time for the actual engineering. Also AI was used for grammer and formatting the ui in `finmatches()`