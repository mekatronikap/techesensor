from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
import datetime

from sqlalchemy.orm import relationship

from database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    company = Column(String, unique=True)
    role = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String, nullable=True)

    sensors = relationship("Sensors", back_populates="owner")


class Sensors(Base):
    __tablename__ = 'sensors'

    id = Column(Integer, primary_key=True)
    description = Column(String)
    type = Column(String)
    site = Column(String)
    equipment = Column(String)
    compartment = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("Users", back_populates="sensors")


class Values(Base):
    __tablename__ = 'wear_values'

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, default=datetime.datetime.utcnow())
    temperature = Column(Integer)
    debris = Column(Integer)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))
