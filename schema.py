from typing import List, Optional
import strawberry
from datetime import datetime, timezone
from sqlalchemy.orm import Session as DBSession

# Local imports
from database import SessionLocal
import models

# --- Input Types ---
@strawberry.input
class StartSessionInput:
    lot_id: int
    spot_id: int
    vehicle_id: int

@strawberry.input
class EndSessionInput:
    session_id: int

# --- GraphQL Object Types ---
@strawberry.type
class Session:
    id: int
    spot_id: int
    vehicle_id: int
    entry_time: datetime
    exit_time: Optional[datetime]
    total_fee: Optional[float]
    status: str

    @strawberry.field
    def spot(self) -> Optional['Spot']:
        db: DBSession = SessionLocal()
        db_spot = db.query(models.Spot).filter(models.Spot.id == self.spot_id).first()
        db.close()
        if not db_spot:
            return None
        return Spot(
            id=db_spot.id,
            lot_id=db_spot.lot_id,
            spot_number=db_spot.spot_number,
            type=db_spot.type,
            status=db_spot.status
        )

    @strawberry.field
    def vehicle(self) -> Optional['Vehicle']:
        db: DBSession = SessionLocal()
        db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == self.vehicle_id).first()
        db.close()
        if not db_vehicle:
            return None
        return Vehicle(
            id=db_vehicle.id,
            license_plate=db_vehicle.license_plate,
            make=db_vehicle.make,
            model=db_vehicle.model,
            color=db_vehicle.color,
            owner_id=db_vehicle.owner_id
        )

@strawberry.type
class Spot:
    id: int
    lot_id: int
    spot_number: str
    type: str
    status: str

@strawberry.type
class Vehicle:
    id: int
    license_plate: str
    make: str
    model: str
    color: str
    owner_id: int

    @strawberry.field
    def sessions(self) -> List[Session]:
        db: DBSession = SessionLocal()
        db_sessions = db.query(models.Session).filter(models.Session.vehicle_id == self.id).all()
        result = [
            Session(
                id=s.id,
                spot_id=s.spot_id,
                vehicle_id=s.vehicle_id,
                entry_time=s.entry_time,
                exit_time=s.exit_time,
                total_fee=s.total_fee,
                status=s.status
            )
            for s in db_sessions
        ]
        db.close()
        return result

@strawberry.type
class ParkingLot:
    id: int
    name: str
    address: str
    total_spots: int
    hourly_rate: float

    @strawberry.field
    def spots(self) -> List[Spot]:
        db: DBSession = SessionLocal()
        db_spots = db.query(models.Spot).filter(models.Spot.lot_id == self.id).all()
        result = [
            Spot(
                id=s.id,
                lot_id=s.lot_id,
                spot_number=s.spot_number,
                type=s.type,
                status=s.status
            )
            for s in db_spots
        ]
        db.close()
        return result

    @strawberry.field
    def available_spots(self) -> int:
        db: DBSession = SessionLocal()
        avail = db.query(models.Spot).filter(models.Spot.lot_id == self.id, models.Spot.status == "available").count()
        db.close()
        return avail

    @strawberry.field
    def occupied_spots(self) -> int:
        db: DBSession = SessionLocal()
        occupied = db.query(models.Spot).filter(models.Spot.lot_id == self.id, models.Spot.status == "occupied").count()
        db.close()
        return occupied

    @strawberry.field
    def lot_status(self) -> str:
        db: DBSession = SessionLocal()
        total = db.query(models.Spot).filter(models.Spot.lot_id == self.id).count()
        occupied = db.query(models.Spot).filter(models.Spot.lot_id == self.id, models.Spot.status == "occupied").count()
        db.close()
        if total == 0:
            return "Empty"
        ratio = occupied / total
        if ratio == 1.0:
            return "Full"
        elif ratio >= 0.8:
            return "Almost Full"
        elif occupied == 0:
            return "Empty"
        else:
            return "Available"

@strawberry.type
class StartSessionPayload:
    session: Session
    parking_lot: Optional[ParkingLot]

@strawberry.type
class EndSessionPayload:
    session: Session

# --- Query & Mutation Types ---
@strawberry.type
class Query:
    @strawberry.field
    def parking_lot(self, id: int) -> Optional[ParkingLot]:
        db: DBSession = SessionLocal()
        lot = db.query(models.ParkingLot).filter(models.ParkingLot.id == id).first()
        if not lot:
            db.close()
            return None
        result = ParkingLot(
            id=lot.id,
            name=lot.name,
            address=lot.address,
            total_spots=lot.total_spots,
            hourly_rate=lot.hourly_rate
        )
        db.close()
        return result

    @strawberry.field
    def vehicle(self, id: int) -> Optional[Vehicle]:
        db: DBSession = SessionLocal()
        v = db.query(models.Vehicle).filter(models.Vehicle.id == id).first()
        if not v:
            db.close()
            return None
        result = Vehicle(
            id=v.id,
            license_plate=v.license_plate,
            make=v.make,
            model=v.model,
            color=v.color,
            owner_id=v.owner_id
        )
        db.close()
        return result

    @strawberry.field
    def active_sessions(self) -> List[Session]:
        db: DBSession = SessionLocal()
        sessions = db.query(models.Session).filter(models.Session.status == "active").all()
        result = [
            Session(
                id=s.id,
                spot_id=s.spot_id,
                vehicle_id=s.vehicle_id,
                entry_time=s.entry_time,
                exit_time=s.exit_time,
                total_fee=s.total_fee,
                status=s.status
            )
            for s in sessions
        ]
        db.close()
        return result

@strawberry.type
class Mutation:
    @strawberry.mutation
    def start_session(self, input: StartSessionInput) -> StartSessionPayload:
        db: DBSession = SessionLocal()
        
        # Ensure spot exists and is available
        spot = db.query(models.Spot).filter(models.Spot.id == input.spot_id).first()
        if not spot:
            db.close()
            raise Exception(f"Spot with ID {input.spot_id} not found")
        if spot.status != "available":
            db.close()
            raise Exception(f"Spot {spot.spot_number} is not available (Status: {spot.status})")
        
        # Ensure vehicle exists
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == input.vehicle_id).first()
        if not vehicle:
            db.close()
            raise Exception(f"Vehicle with ID {input.vehicle_id} not found")

        # Update spot status
        spot.status = "occupied"
        
        # Create session
        new_session = models.Session(
            spot_id=input.spot_id,
            vehicle_id=input.vehicle_id,
            entry_time=datetime.now(timezone.utc).replace(tzinfo=None),
            status="active"
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        result = Session(
            id=new_session.id,
            spot_id=new_session.spot_id,
            vehicle_id=new_session.vehicle_id,
            entry_time=new_session.entry_time,
            exit_time=new_session.exit_time,
            total_fee=new_session.total_fee,
            status=new_session.status
        )

        # Build updated parking lot object to show new availability counts
        db2: DBSession = SessionLocal()
        lot_db = db2.query(models.ParkingLot).filter(models.ParkingLot.id == input.lot_id).first()
        updated_lot = None
        if lot_db:
            updated_lot = ParkingLot(
                id=lot_db.id,
                name=lot_db.name,
                address=lot_db.address,
                total_spots=lot_db.total_spots,
                hourly_rate=lot_db.hourly_rate
            )
        db2.close()
        db.close()
        return StartSessionPayload(session=result, parking_lot=updated_lot)

    @strawberry.mutation
    def end_session(self, input: EndSessionInput) -> EndSessionPayload:
        db: DBSession = SessionLocal()
        
        session = db.query(models.Session).filter(models.Session.id == input.session_id).first()
        if not session or session.status != "active":
            db.close()
            raise Exception("Session is not active or does not exist")
        
        # Find lot hourly rate to calculate fees
        spot = db.query(models.Spot).filter(models.Spot.id == session.spot_id).first()
        lot = db.query(models.ParkingLot).filter(models.ParkingLot.id == spot.lot_id).first()
        
        exit_time = datetime.now(timezone.utc).replace(tzinfo=None)
        duration_hours = (exit_time - session.entry_time).total_seconds() / 3600
        # Charge for at least 1 hour
        rate = lot.hourly_rate if lot else 5.0 # Fallback rate
        total_fee = max(1.0, duration_hours) * rate
        
        # Update session
        session.exit_time = exit_time
        session.total_fee = round(total_fee, 2)
        session.status = "completed"
        
        # Free up the spot
        spot.status = "available"
        
        db.commit()
        db.refresh(session)
        
        result = Session(
            id=session.id,
            spot_id=session.spot_id,
            vehicle_id=session.vehicle_id,
            entry_time=session.entry_time,
            exit_time=session.exit_time,
            total_fee=session.total_fee,
            status=session.status
        )
        db.close()
        return EndSessionPayload(session=result)

schema = strawberry.Schema(query=Query, mutation=Mutation)
