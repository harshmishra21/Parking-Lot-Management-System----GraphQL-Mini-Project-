import asyncio
from schema import schema
from database import SessionLocal
import models

queries = [
    """
    query {
      parkingLot(id: 1) {
        name
        availableSpots
        spots {
          spotNumber
          type
          status
        }
      }
    }
    """,
    """
    query {
      vehicle(id: 1) {
        licensePlate
        sessions {
          entryTime
          exitTime
          totalFee
        }
      }
    }
    """,
    """
    query {
      activeSessions {
        spot { spotNumber }
        vehicle { licensePlate }
        entryTime
      }
    }
    """,
    """
    mutation {
      startSession(input: {
        lotId: 1
        spotId: 3
        vehicleId: 1
      }) {
        session {
          id
          entryTime
          status
        }
      }
    }
    """,
    """
    mutation {
      endSession(input: {
        sessionId: 5
      }) {
        session {
          id
          exitTime
          totalFee
        }
      }
    }
    """
]

for i, q in enumerate(queries):
    print(f"\\n--- Running Query {i+1} ---")
    result = schema.execute_sync(q)
    if result.errors:
        print("ERRORS:", result.errors)
    else:
        print("DATA:", result.data)
