# 🅿️ Parking Lot API - Test Queries (English Guide)

This file contains all **5 main GraphQL queries** that you can copy-paste directly into the playground to test.

**Open Playground:** [http://localhost:8001/graphql](http://localhost:8001/graphql)

> ⚠️ **Important Tip:** Before pasting each query, press `Cmd + A` (select all) in the editor, delete the old text, **then** paste the new query. Otherwise, you'll get a syntax error!

---

## 🔍 Query 1 — Complete Parking Lot Status

**What does this do?**
This query tells you:
- How many spots are **available**
- How many spots are **occupied**
- What is the **overall status** of the lot — `"Available"`, `"Almost Full"`, `"Full"`, or `"Empty"`
- The **number, type and status** of each individual spot

Basically, this single query gives you a full LIVE picture of the parking lot! 🎯

```graphql
query {
  parkingLot(id: 1) {
    name
    totalSpots
    availableSpots
    occupiedSpots
    lotStatus
    spots {
      spotNumber
      type
      status
    }
  }
}
```

**Expected Result:** `"lotStatus": "Available"` — Out of 20 spots at Downtown Central Parking, ~18 will be available (after seeding).

---

## 🚗 Query 2 — Full Vehicle Parking History

**What does this do?**
Shows the complete parking record for any specific vehicle (here, the Tesla with ID 1):
- **entryTime** of each session
- **exitTime**
- **totalFee** paid
- **status** (completed or still active)

The vehicle's entire history in one go! 📋

```graphql
query {
  vehicle(id: 1) {
    licensePlate
    make
    sessions {
      entryTime
      exitTime
      totalFee
      status
    }
  }
}
```

**Expected Result:** You will see completed sessions and fees for the Tesla with `"licensePlate": "XYZ-123"`.

---

## 🔴 Query 3 — Who is Currently Parked? (Live Active Sessions)

**What does this do?**
Returns a full list of vehicles currently parked in the lot in real-time:
- **Session ID** (unique number)
- **entryTime** — when the vehicle entered
- **exitTime** — will be `null` for active sessions (vehicle hasn't left yet)
- **spotNumber** and **status** of the spot
- Vehicle's **licensePlate**

Security or attendants can use this query to check who is in the parking lot! 👀

```graphql
query {
  activeSessions {
    id
    entryTime
    exitTime
    status
    spot {
      spotNumber
      status
    }
    vehicle {
      licensePlate
    }
  }
}
```

**Expected Result:** There will be 2 active sessions (after seeding) — vehicles LMN-456 and EVR-777.

---

## 🟢 Query 4 — Start a New Parking Session (Vehicle Entry)

**What does this do?**
Run this mutation when a new vehicle enters the parking lot. This:
- Creates a **new session**
- Automatically sets **entryTime** (current time)
- Sets **exitTime** to `null` (vehicle is inside)
- Updates spot status to `"occupied"`

> ⚠️ **Note:** `spotId: 3` will only work if the spot is available. Run Query 1 first to check which spot is `"available"`, then enter that `spotId` here!

```graphql
mutation {
  startSession(input: {
    lotId: 1
    spotId: 3
    vehicleId: 1
  }) {
    session {
      id
      entryTime
      exitTime
      status
    }
  }
}
```

**Expected Result:** New session created, `"status": "active"`, `"exitTime": null`. **Note the `id` from the response — you'll need it in Query 5!**

---

## 🔴 Query 5 — End Parking Session (Vehicle Exit)

**What does this do?**
Run this mutation when a vehicle leaves. This:
- Automatically sets **exitTime** (current time)
- Calculates **totalFee** (hourly basis — minimum 1 hour charge)
- Updates session **status** to `"completed"`
- Sets spot back to `"available"`

> ⚠️ **Run Query 4 first**, then use the `id` from that response (e.g., `5`) in place of `sessionId` here!

```graphql
mutation {
  endSession(input: {
    sessionId: 5
  }) {
    session {
      id
      entryTime
      exitTime
      totalFee
      status
    }
  }
}
```

**Expected Result:** `"status": "completed"`, `"totalFee": 5.0` (Minimum 1 hour charge × $5/hr rate).

---

## ✅ Run in Correct Order

For the best experience, run queries in this order:

```
Query 1 → Check which spots are available
Query 2 → Check a vehicle's history
Query 3 → Check who is currently in the lot
Query 4 → Start a new session (entry) → Note the ID!
Query 5 → End the session (exit) → Use the ID from Query 4
```

---

## 🔄 Need Fresh Data? Re-seed the Database

If the database has too many test sessions and you want a clean start, run this command in the terminal:

```bash
python seed.py
```

This removes all old data and loads fresh demo data. Then restart the server:

```bash
uvicorn main:app --reload
```
