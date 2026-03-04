import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def seed_data():
    # Recreate the database structure
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Create a Parking Lot
        lot = models.ParkingLot(
            name="Downtown Central Parking",
            address="123 Main St, Cityville",
            total_spots=50,
            hourly_rate=5.0
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)

        # Create Spots for the lot (20 spots)
        for i in range(1, 21):
            spot_type = "electric" if i <= 4 else "compact" if i <= 10 else "standard"
            db.add(models.Spot(
                lot_id=lot.id,
                spot_number=f"A{i:02d}",
                type=spot_type,
                status="available"
            ))
        db.commit()

        spots = db.query(models.Spot).all()

        # Create 6 Owners
        owners_data = [
            {"name": "Alice Smith", "email": "alice@example.com", "phone": "555-0100", "subscription_type": "premium"},
            {"name": "Bob Johnson", "email": "bob@example.com", "phone": "555-0101", "subscription_type": "basic"},
            {"name": "Charlie Brown", "email": "charlie@example.com", "phone": "555-0102", "subscription_type": "none"},
            {"name": "Diana Ross", "email": "diana@example.com", "phone": "555-0103", "subscription_type": "premium"},
            {"name": "Evan Wright", "email": "evan@example.com", "phone": "555-0104", "subscription_type": "basic"},
            {"name": "Fiona Green", "email": "fiona@example.com", "phone": "555-0105", "subscription_type": "none"},
        ]
        owners = []
        for o_data in owners_data:
            o = models.Owner(**o_data)
            db.add(o)
            owners.append(o)
        db.commit()
        for o in owners: db.refresh(o)

        # Create 6 Vehicles
        vehicles_data = [
            {"license_plate": "XYZ-123", "make": "Tesla", "model": "Model 3", "color": "White", "owner_id": owners[0].id},
            {"license_plate": "ABC-987", "make": "Honda", "model": "Civic", "color": "Blue", "owner_id": owners[1].id},
            {"license_plate": "LMN-456", "make": "Ford", "model": "F-150", "color": "Black", "owner_id": owners[2].id},
            {"license_plate": "EVR-777", "make": "Rivian", "model": "R1T", "color": "Green", "owner_id": owners[3].id},
            {"license_plate": "QWE-111", "make": "Toyota", "model": "Corolla", "color": "Silver", "owner_id": owners[4].id},
            {"license_plate": "ZXC-999", "make": "Chevrolet", "model": "Bolt", "color": "Red", "owner_id": owners[5].id},
        ]
        vehicles = []
        for v_data in vehicles_data:
            v = models.Vehicle(**v_data)
            db.add(v)
            vehicles.append(v)
        db.commit()
        for v in vehicles: db.refresh(v)
        
        # Create past sessions for history
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) # Keep naive for sqlite but fix deprecation warning
        
        db.add(models.Session(
            spot_id=spots[0].id, vehicle_id=vehicles[0].id,
            entry_time=now - datetime.timedelta(hours=5),
            exit_time=now - datetime.timedelta(hours=2),
            total_fee=15.0, status="completed"
        ))
        
        db.add(models.Session(
            spot_id=spots[5].id, vehicle_id=vehicles[1].id,
            entry_time=now - datetime.timedelta(hours=24),
            exit_time=now - datetime.timedelta(hours=22),
            total_fee=10.0, status="completed"
        ))
        
        # Create active sessions
        # vehicle 2 is currently parked
        spots[10].status = "occupied"
        db.add(models.Session(
            spot_id=spots[10].id, vehicle_id=vehicles[2].id,
            entry_time=now - datetime.timedelta(hours=1),
            status="active"
        ))
        
        # vehicle 3 (Rivian) is currently charging
        spots[1].status = "occupied"
        db.add(models.Session(
            spot_id=spots[1].id, vehicle_id=vehicles[3].id,
            entry_time=now - datetime.timedelta(minutes=30),
            status="active"
        ))
        
        db.commit()

        print("Database seeded effectively! Lots, 20 Spots, 6 Owners, 6 Vehicles, and history have been imported.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
