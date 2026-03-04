from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    total_spots = Column(Integer)
    hourly_rate = Column(Float)

    spots = relationship("Spot", back_populates="lot")


class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    spot_number = Column(String, index=True)
    type = Column(String)  # standard, compact, electric
    status = Column(String, default="available")  # available, occupied, reserved, maintenance

    lot = relationship("ParkingLot", back_populates="spots")
    sessions = relationship("Session", back_populates="spot")


class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    subscription_type = Column(String, default="none")
    
    vehicles = relationship("Vehicle", back_populates="owner")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    make = Column(String)
    model = Column(String)
    color = Column(String)
    owner_id = Column(Integer, ForeignKey("owners.id"))

    owner = relationship("Owner", back_populates="vehicles")
    sessions = relationship("Session", back_populates="vehicle")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("spots.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    entry_time = Column(DateTime)
    exit_time = Column(DateTime, nullable=True)
    total_fee = Column(Float, nullable=True)
    status = Column(String, default="active")  # active, completed, overdue

    spot = relationship("Spot", back_populates="sessions")
    vehicle = relationship("Vehicle", back_populates="sessions")
