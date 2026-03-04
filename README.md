# 🅿️ Parking Lot Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![GraphQL](https://img.shields.io/badge/GraphQL-Strawberry-E10098?logo=graphql&logoColor=white)](https://strawberry.rocks/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-featured **GraphQL API** for managing parking lots, spots, vehicles, owners, and real-time parking sessions — built with **FastAPI**, **Strawberry GraphQL**, **SQLAlchemy**, and **SQLite**.

This project was designed as a practical, end-to-end backend system that handles the complete lifecycle of a parking session: from a vehicle entering a spot, to fee calculation on exit, to real-time availability tracking.

---

## 📑 Table of Contents

- [Features](#-features)
- [Project Architecture](#-project-architecture)
- [File Structure](#-file-structure)
- [Database Schema](#-database-schema)
- [Technologies Used](#-technologies--libraries-used)
- [Setup & Installation](#-setup--installation)
- [Running the Server](#-running-the-server)
- [GraphQL Playground](#-graphql-playground)
- [GraphQL Queries & Mutations (5 Core Queries)](#-graphql-queries--mutations-5-core-queries)
- [Seed Data Overview](#-seed-data-overview)
- [API Endpoints](#-api-endpoints)
- [Business Logic](#-business-logic)
- [Error Handling](#-error-handling)
- [GitHub / Git Safety Notes](#-github--git-safety-notes)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

---

## ✨ Features

- 🔍 **Real-time Parking Status** — Query full parking lot status including total, available, and occupied spots
- 🚗 **Vehicle Management** — Track vehicles by license plate, make, model, and color
- 👤 **Owner Profiles** — Each vehicle is linked to an owner with subscription plans (none / basic / premium)
- 🅿️ **Spot Type Classification** — Three spot types: `standard`, `compact`, and `electric`
- ⏱️ **Session Lifecycle Management** — Start and end parking sessions with automatic timestamping
- 💰 **Automatic Fee Calculation** — Fees are calculated based on hourly rate × duration (minimum 1 hour charge)
- 📊 **Live Session Monitoring** — Query all currently active (occupied) parking sessions
- 📜 **Vehicle Parking History** — Full history of all past sessions for any registered vehicle
- 🏷️ **Lot Status Labels** — Smart status labels: `Available`, `Almost Full`, `Full`, or `Empty`
- 🎮 **Interactive GraphQL Playground** — Built-in browser-based UI at `/graphql`

---

## 🏗️ Project Architecture

```
Client (Browser / App)
        │
        ▼
  FastAPI Web Server  (main.py)
        │
        ▼
  GraphQL Router  (Strawberry @ /graphql)
        │
        ▼
  Schema Layer  (schema.py)  →  Query / Mutation resolvers
        │
        ▼
  Models Layer  (models.py)  →  SQLAlchemy ORM models
        │
        ▼
  Database Layer  (database.py)  →  SQLite (parking.db)
```

**Request Flow:**
1. Client sends a GraphQL query or mutation via HTTP POST to `/graphql`
2. FastAPI routes the request through Strawberry's `GraphQLRouter`
3. Strawberry resolves the query using Python resolver functions in `schema.py`
4. Resolvers query the SQLite database via SQLAlchemy ORM in `models.py`
5. Data is serialized into GraphQL types and returned as JSON to the client

---

## 📁 File Structure

```
Parking lot management system/
│
├── main.py             # FastAPI app entry point — mounts GraphQL router
├── schema.py           # All GraphQL types, queries, and mutations
├── models.py           # SQLAlchemy ORM models (database table definitions)
├── database.py         # Database engine, session factory, and Base class
├── seed.py             # Database seeder — populates demo data
├── test_queries.py     # Script to run all 5 queries programmatically
│
├── README.md           # This file — complete project documentation
├── test_readme.md      # Secondary quick-reference guide for queries
│
├── parking.db          # SQLite database file (auto-created, NOT committed to git)
├── .gitignore          # Files excluded from git (venv, db, cache)
│
└── venv/               # Python virtual environment (NOT committed to git)
```

### File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | Creates the FastAPI app, mounts the Strawberry GraphQL router at `/graphql`, auto-creates DB tables on startup |
| `schema.py` | Defines all GraphQL object types (`ParkingLot`, `Spot`, `Vehicle`, `Session`), input types, queries (`parkingLot`, `vehicle`, `activeSessions`), and mutations (`startSession`, `endSession`) |
| `models.py` | Defines 4 SQLAlchemy models: `ParkingLot`, `Spot`, `Owner`, `Vehicle`, `Session` with their columns, relationships, and foreign keys |
| `database.py` | Sets up the SQLite connection URL, creates the SQLAlchemy engine, session factory (`SessionLocal`), and declarative `Base` class |
| `seed.py` | Drops and recreates the database, then inserts: 1 parking lot, 20 spots, 6 owners, 6 vehicles, 2 completed sessions, and 2 active sessions |
| `test_queries.py` | Runs all 5 GraphQL queries directly against the schema (without HTTP) using `schema.execute_sync()` |

---

## 🗄️ Database Schema

The system uses **5 tables** in a SQLite database file (`parking.db`):

### `parking_lots`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `name` | STRING | Name of the parking lot (e.g., "Downtown Central Parking") |
| `address` | STRING | Physical address of the lot |
| `total_spots` | INTEGER | Total number of spots in the lot |
| `hourly_rate` | FLOAT | Fee charged per hour (e.g., `5.0` = ₹5/hr) |

### `spots`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `lot_id` | INTEGER (FK → parking_lots.id) | Which lot this spot belongs to |
| `spot_number` | STRING | Human-readable label (e.g., "A01", "A12") |
| `type` | STRING | Spot category: `electric`, `compact`, or `standard` |
| `status` | STRING | Current state: `available`, `occupied`, `reserved`, or `maintenance` |

**Spot Type Distribution (Seeded):**
- Spots A01–A04 → `electric` (for EVs)
- Spots A05–A10 → `compact`
- Spots A11–A20 → `standard`

### `owners`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `name` | STRING | Full name of the vehicle owner |
| `email` | STRING (unique) | Email address |
| `phone` | STRING | Contact phone number |
| `subscription_type` | STRING | Subscription plan: `none`, `basic`, or `premium` |

### `vehicles`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `license_plate` | STRING (unique) | Vehicle registration plate (e.g., "XYZ-123") |
| `make` | STRING | Vehicle manufacturer (e.g., "Tesla", "Honda") |
| `model` | STRING | Vehicle model name (e.g., "Model 3", "Civic") |
| `color` | STRING | Vehicle color |
| `owner_id` | INTEGER (FK → owners.id) | Owner of this vehicle |

### `sessions`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `spot_id` | INTEGER (FK → spots.id) | Which spot was used |
| `vehicle_id` | INTEGER (FK → vehicles.id) | Which vehicle parked |
| `entry_time` | DATETIME | When the vehicle entered (UTC, auto-set) |
| `exit_time` | DATETIME (nullable) | When the vehicle left (`null` if still active) |
| `total_fee` | FLOAT (nullable) | Calculated fee on exit (`null` if still active) |
| `status` | STRING | Session state: `active`, `completed`, or `overdue` |

### Entity Relationships

```
ParkingLot ──< Spot ──< Session >── Vehicle >── Owner
```
- One `ParkingLot` has many `Spots`
- One `Spot` has many `Sessions`
- One `Vehicle` has many `Sessions`
- One `Owner` has many `Vehicles`

---

## 🛠️ Technologies & Libraries Used

| Library | Version | Purpose |
|---------|---------|---------|
| [Python 3](https://www.python.org/) | 3.10+ | Core programming language |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.100+ | High-performance async web framework for building the API |
| [Strawberry GraphQL](https://strawberry.rocks/) | Latest | Python-first GraphQL library using Python type annotations for schema definition |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.x | ORM toolkit for defining database models as Python classes and querying without raw SQL |
| [SQLite](https://www.sqlite.org/) | Built-in | Lightweight file-based relational database — no server installation required |
| [Uvicorn](https://www.uvicorn.org/) | Latest | ASGI web server to run the FastAPI application locally |

### Why These Technologies?

- **FastAPI** was chosen for its automatic API documentation, async support, and speed (one of the fastest Python frameworks)
- **Strawberry** was chosen over Graphene because it uses Python type hints natively, making the schema code cleaner and more Pythonic
- **SQLAlchemy ORM** abstracts away raw SQL, making it easy to define table relationships as Python class attributes
- **SQLite** was chosen for its zero-configuration setup — perfect for a local/demo system. Can easily be swapped for PostgreSQL/MySQL in production
- **Uvicorn** is the recommended ASGI server for FastAPI, supporting hot-reload during development

---

## ⚙️ Setup & Installation

### Prerequisites

- **Python 3.10 or higher** — [Download here](https://www.python.org/downloads/)
- **pip** (comes with Python)
- A terminal / command prompt

### Step-by-Step Setup

**Step 1: Clone the Repository**
```bash
git clone https://github.com/yourusername/parking-lot-management-system.git
cd "parking-lot-management-system"
```

**Step 2: Create a Virtual Environment**

A virtual environment keeps dependencies isolated from your system Python.

```bash
python3 -m venv venv
```

**Step 3: Activate the Virtual Environment**

On **macOS / Linux:**
```bash
source venv/bin/activate
```

On **Windows:**
```cmd
venv\Scripts\activate
```

> 💡 You should see `(venv)` appear in your terminal prompt when the environment is active.

**Step 4: Install All Dependencies**
```bash
pip install fastapi "uvicorn[standard]" strawberry-graphql sqlalchemy
```

This installs all 4 required libraries. No `requirements.txt` is needed for this project, but you can generate one with:
```bash
pip freeze > requirements.txt
```

**Step 5: Seed the Database with Demo Data**

This creates the `parking.db` SQLite file and populates it with:
- 1 Parking Lot
- 20 Parking Spots (4 electric, 6 compact, 10 standard)
- 6 Owners with different subscription tiers
- 6 Vehicles (Tesla, Honda, Ford, Rivian, Toyota, Chevrolet)
- 2 Completed parking sessions (with fees)
- 2 Active parking sessions (vehicles currently parked)

```bash
python seed.py
```

Expected output:
```
Database seeded effectively! Lots, 20 Spots, 6 Owners, 6 Vehicles, and history have been imported.
```

---

## 🚀 Running the Server

Start the GraphQL API server with hot-reload enabled:

```bash
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

> The `--reload` flag means the server automatically restarts whenever you save a code change. Remove it for production deployments.

**To stop the server:** Press `Ctrl + C` in the terminal.

---

## 🎮 GraphQL Playground

Once the server is running, open your browser and visit:

**👉 [http://localhost:8000/graphql](http://localhost:8000/graphql)**

This opens Strawberry's built-in **GraphiQL** interactive playground where you can:
- Write and run GraphQL queries and mutations
- Browse the full interactive schema documentation (click the book icon)
- See auto-complete suggestions as you type
- View exact response JSON

> **How to use the playground:**
> 1. Click inside the left (input) panel
> 2. Press `Cmd+A` (Mac) or `Ctrl+A` (Windows) to select all
> 3. Paste your query
> 4. Click the ▶️ Play button (or press `Ctrl+Enter`)

The root API response is available at: [http://localhost:8000/](http://localhost:8000/)

---

## 🔍 GraphQL Queries & Mutations (5 Core Queries)

These are the 5 primary operations supported by the API. Run them in this order for the best testing experience:

---

### Query 1 — Get Full Parking Lot Status 🏢

**What it does:**
Fetches the complete live status of a parking lot by its ID. Returns:
- Lot name and address
- Total spots, available count, occupied count
- Smart status label: `Available`, `Almost Full`, `Full`, or `Empty`
- A list of every individual spot with its number, type, and current status

**When to use:** To see which spots are free before starting a new session.

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

**Expected Response (after seeding):**
```json
{
  "data": {
    "parkingLot": {
      "name": "Downtown Central Parking",
      "totalSpots": 20,
      "availableSpots": 18,
      "occupiedSpots": 2,
      "lotStatus": "Available",
      "spots": [
        { "spotNumber": "A01", "type": "electric", "status": "available" },
        { "spotNumber": "A02", "type": "electric", "status": "occupied" },
        ...
      ]
    }
  }
}
```

**How `lotStatus` is calculated:**
| Condition | Label |
|-----------|-------|
| 0 occupied | `Empty` |
| > 0 but < 80% full | `Available` |
| ≥ 80% full | `Almost Full` |
| 100% full | `Full` |

---

### Query 2 — Get Vehicle Parking History 🚗

**What it does:**
Looks up a specific vehicle by its database ID and returns:
- License plate and vehicle make
- Full list of all past and current parking sessions
- For each session: entry time, exit time, total fee paid, and session status

**When to use:** To audit a vehicle's parking history or verify past charges.

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

**Expected Response:**
```json
{
  "data": {
    "vehicle": {
      "licensePlate": "XYZ-123",
      "make": "Tesla",
      "sessions": [
        {
          "entryTime": "2025-03-04T20:00:00",
          "exitTime": "2025-03-04T23:00:00",
          "totalFee": 15.0,
          "status": "completed"
        }
      ]
    }
  }
}
```

> **Note:** Vehicle ID 1 is the Tesla Model 3 (license plate: XYZ-123) seeded by default.

---

### Query 3 — View All Active (Live) Sessions 🔴

**What it does:**
Returns all parking sessions that are currently `active` — meaning the vehicle is still parked and has not exited yet. Returns for each active session:
- Session ID, entry time, exit time (will be `null` since still active), status
- The spot's number and status
- The vehicle's license plate

**When to use:** For parking attendants or security to monitor who is currently parked.

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

**Expected Response (after seeding):**
```json
{
  "data": {
    "activeSessions": [
      {
        "id": 3,
        "entryTime": "2025-03-05T00:00:00",
        "exitTime": null,
        "status": "active",
        "spot": { "spotNumber": "A11", "status": "occupied" },
        "vehicle": { "licensePlate": "LMN-456" }
      },
      {
        "id": 4,
        "entryTime": "2025-03-05T00:30:00",
        "exitTime": null,
        "status": "active",
        "spot": { "spotNumber": "A02", "status": "occupied" },
        "vehicle": { "licensePlate": "EVR-777" }
      }
    ]
  }
}
```

> After seeding, 2 active sessions exist: LMN-456 (Ford F-150) and EVR-777 (Rivian R1T).

---

### Query 4 — Start a New Parking Session (Vehicle Entry) 🟢

**What it does:**
A **mutation** that registers a new vehicle entering the parking lot. It:
1. Validates that the specified spot exists and is `available`
2. Validates that the specified vehicle exists in the database
3. Updates the spot status to `occupied`
4. Creates a new `Session` record with `entry_time` set to the current UTC time and `status` set to `active`
5. Returns the new session ID, entry time, exit time (`null`), and status

**Required inputs:**
- `lotId` — ID of the parking lot (use `1` for demo)
- `spotId` — ID of an **available** spot (check Query 1 first!)
- `vehicleId` — ID of the vehicle entering

> ⚠️ **Important:** Always run Query 1 first to find an available spot ID. `spotId: 3` is used below as an example — it may already be occupied if you've run this mutation before. Re-seed if needed.

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

**Expected Response:**
```json
{
  "data": {
    "startSession": {
      "session": {
        "id": 5,
        "entryTime": "2025-03-05T01:06:30",
        "exitTime": null,
        "status": "active"
      }
    }
  }
}
```

> 📌 **Note the `id` returned** (e.g., `5`) — you will need it for Query 5 to end this session!

**Error Cases:**
- `Spot with ID X not found` — Invalid spot ID
- `Spot A03 is not available (Status: occupied)` — Spot is already taken

---

### Query 5 — End a Parking Session (Vehicle Exit) 🔴

**What it does:**
A **mutation** that processes a vehicle's exit. It:
1. Looks up the session by `sessionId` and verifies it is `active`
2. Records the current UTC time as `exit_time`
3. Calculates `total_fee` using: `max(1.0, duration_in_hours) × hourly_rate`
   - Minimum charge: 1 full hour (even if the car stayed for only 10 minutes)
   - Rate for the demo lot: ₹5.00/hour
4. Updates the session `status` to `completed`
5. Frees up the spot (sets spot status back to `available`)

**Required input:**
- `sessionId` — The ID returned from Query 4's `startSession` response

> ⚠️ **Important:** Use the session ID from Query 4's response. The `sessionId: 5` below is an example. Always use the actual ID that was returned to you.

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

**Expected Response:**
```json
{
  "data": {
    "endSession": {
      "session": {
        "id": 5,
        "entryTime": "2025-03-05T01:06:30",
        "exitTime": "2025-03-05T01:10:00",
        "totalFee": 5.0,
        "status": "completed"
      }
    }
  }
}
```

> `totalFee: 5.0` = minimum 1 hour charge × ₹5/hr rate.

**Error Cases:**
- `Session is not active or does not exist` — Session ID is wrong, or it was already ended

---

### ✅ Recommended Query Execution Order

For the best end-to-end testing experience, run the queries in this sequence:

```
Step 1  →  Query 1  →  Check which spots are available
Step 2  →  Query 2  →  View a vehicle's history
Step 3  →  Query 3  →  See who is currently parked
Step 4  →  Query 4  →  Start a new session (vehicle enters) → NOTE the session ID!
Step 5  →  Query 5  →  End the session (vehicle exits) → USE the session ID from Step 4
```

---

## 🌱 Seed Data Overview

Running `python seed.py` populates the database with this demo data:

### Parking Lot
| Field | Value |
|-------|-------|
| Name | Downtown Central Parking |
| Address | 123 Main St, Cityville |
| Total Spots | 50 (20 created) |
| Hourly Rate | ₹5.00 / hr |

### Owners (6 total)
| Name | Email | Subscription |
|------|-------|--------------|
| Alice Smith | alice@example.com | premium |
| Bob Johnson | bob@example.com | basic |
| Charlie Brown | charlie@example.com | none |
| Diana Ross | diana@example.com | premium |
| Evan Wright | evan@example.com | basic |
| Fiona Green | fiona@example.com | none |

### Vehicles (6 total)
| ID | License Plate | Make | Model | Color | Owner |
|----|--------------|------|-------|-------|-------|
| 1 | XYZ-123 | Tesla | Model 3 | White | Alice |
| 2 | ABC-987 | Honda | Civic | Blue | Bob |
| 3 | LMN-456 | Ford | F-150 | Black | Charlie |
| 4 | EVR-777 | Rivian | R1T | Green | Diana |
| 5 | QWE-111 | Toyota | Corolla | Silver | Evan |
| 6 | ZXC-999 | Chevrolet | Bolt | Red | Fiona |

### Pre-seeded Sessions
| Session | Vehicle | Status | Duration | Fee |
|---------|---------|--------|----------|-----|
| 1 | Tesla (XYZ-123) | completed | 3 hours | ₹15.0 |
| 2 | Honda (ABC-987) | completed | 2 hours | ₹10.0 |
| 3 | Ford (LMN-456) | **active** | ~1 hour ago | — |
| 4 | Rivian (EVR-777) | **active** | ~30 min ago | — |

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message and navigation hint |
| `/graphql` | GET | Opens the interactive GraphiQL playground |
| `/graphql` | POST | GraphQL query/mutation endpoint (for programmatic clients) |

---

## ⚙️ Business Logic

### Fee Calculation
```python
duration_hours = (exit_time - entry_time).total_seconds() / 3600
total_fee = max(1.0, duration_hours) * hourly_rate
total_fee = round(total_fee, 2)
```
- **Minimum charge:** Always charges for at least 1 full hour
- **Rate:** Determined by the lot's `hourly_rate` field (default: ₹5.00)
- **Rounding:** Fee is rounded to 2 decimal places

### Lot Status Calculation
```python
ratio = occupied_spots / total_spots

if ratio == 1.0  →  "Full"
if ratio >= 0.8  →  "Almost Full"
if ratio == 0.0  →  "Empty"
else             →  "Available"
```

### Session Lifecycle
```
[Spot: available] → startSession() → [Spot: occupied, Session: active]
                          ↓
                    endSession()
                          ↓
               [Spot: available, Session: completed, fee calculated]
```

---

## 🛡️ Error Handling

The API raises descriptive GraphQL errors for invalid operations:

| Scenario | Error Message |
|----------|--------------|
| Spot not found | `Spot with ID {id} not found` |
| Spot already occupied | `Spot {number} is not available (Status: occupied)` |
| Vehicle not found | `Vehicle with ID {id} not found` |
| Session not active / not found | `Session is not active or does not exist` |

All errors are returned in the standard GraphQL `errors` array format.

---

## 🔒 GitHub / Git Safety Notes

The following files are **excluded from git** via `.gitignore` and will **not** be uploaded to GitHub:

| File / Folder | Reason |
|---------------|--------|
| `venv/` | Python virtual environment — very large, not needed on GitHub |
| `venv_fix/` | Secondary test environment |
| `demo_env/` | Demo environment folder |
| `parking.db` | SQLite database — contains runtime data, regenerated via `seed.py` |
| `*.db`, `*.sqlite` | All database files |
| `__pycache__/` | Python bytecode cache — auto-generated |
| `.DS_Store` | macOS system file — irrelevant to the project |

> ✅ **Safe to upload:** `main.py`, `schema.py`, `models.py`, `database.py`, `seed.py`, `test_queries.py`, `README.md`, `test_readme.md`, `.gitignore`

---

## 🔮 Future Improvements

- [ ] **Authentication & Authorization** — JWT tokens for secure API access
- [ ] **PostgreSQL Support** — Replace SQLite with a production-grade database
- [ ] **Subscription Plans** — Apply discounted rates for `basic` and `premium` owners
- [ ] **Reserved Spots** — Allow pre-booking of specific spots
- [ ] **Overdue Session Alerts** — Flag sessions as `overdue` after a maximum duration
- [ ] **Admin Dashboard** — A frontend web app to visualize parking lot status
- [ ] **Multi-Lot Support** — Query across multiple lots at once
- [ ] **Pagination** — Add pagination to session history for large datasets
- [ ] **Email Notifications** — Send entry/exit receipts to registered owners
- [ ] **Docker Support** — Containerize the application for easy deployment

---

## 🧑‍💻 Author

**Harsh Mishra**
- GitHub: [@harshmishra21](https://github.com/harshmishra21)

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

> 💡 **Quick Start Reminder:**
> ```bash
> python3 -m venv venv && source venv/bin/activate
> pip install fastapi "uvicorn[standard]" strawberry-graphql sqlalchemy
> python seed.py
> uvicorn main:app --reload
> # Open: http://localhost:8000/graphql
> ```
