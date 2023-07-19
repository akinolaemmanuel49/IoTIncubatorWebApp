from datetime import datetime, timedelta

from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres@localhost/iotincubatordb", pool_size=15, max_overflow=20)
Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    passwordhash = Column(String, nullable=False)
    role = Column(String(5), nullable=False, default="USER")
    sessions = relationship("SessionData", back_populates="user")

    def get_id(self):
        return self.id
    
    def __repr__(self):
        return f"User(username={self.username})"


class SessionData(Base):
    __tablename__ = "session_data"

    id = Column(Integer, primary_key=True)
    max_temperature = Column(Float, nullable=False)
    min_temperature = Column(Float, nullable=False)
    max_humidity = Column(Float, nullable=False)
    min_humidity = Column(Float, nullable=False)
    turn_interval = Column(Float, default=4.8)
    turn_stage_start = Column(Integer, nullable=False, default=3)
    duration_turning_stage = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    session_start = Column(
        DateTime, default=datetime.utcnow, server_default=func.now())
    session_duration = Column(Integer, nullable=False)
    sensor_data = relationship("SensorData", back_populates="session_data")

    user = relationship("User", back_populates="sessions")
    schedule = relationship("Schedule", back_populates="session")

    def __repr__(self):
        return (
            f"SessionData(turn_interval={self.turn_interval}, "
            f"turn_stage_start={self.turn_stage_start}, "
            f"duration_turning_stage={self.duration_turning_stage}, "
            f"is_active={self.is_active}, "
            f"user_id={self.user_id}, "
            f"session_start={self.session_start}, "
            f"session_duration={self.session_duration})"
        )

    def check_hatch_stage(self):
        current_time = datetime.utcnow()
        turning_stage_end_time = self.session_start + \
            timedelta(days=self.duration_turning_stage + self.turn_stage_start)
        if current_time >= turning_stage_end_time:
            return True
        return False

    def check_turn_stage(self):
        current_time = datetime.utcnow()
        pre_turn_stage = self.session_start + \
            timedelta(days=self.turn_stage_start)
        post_turn_stage = self.session_start + \
            timedelta(days=self.duration_turning_stage)

        if current_time < pre_turn_stage and current_time > post_turn_stage:
            return False
        return True


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)
    temperature = Column(Float)
    humidity = Column(Float)
    refill_water = Column(Boolean)
    motion_detected = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow,
                       server_default=func.now())
    session_id = Column(Integer, ForeignKey("session_data.id"), nullable=False)

    session_data = relationship("SessionData", back_populates="sensor_data")

    def __repr__(self):
        return (
            f"SensorData(temperature={self.temperature}, "
            f"humidity={self.humidity}, "
            f"refill_water={self.refill_water}, "
            f"motion_detected={self.motion_detected}, "
            f"session_id={self.session_id}, "
            f"timestamp={self.timestamp})"
        )


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("session_data.id"))
    session = relationship("SessionData", back_populates="schedule")
    scheduled_time = Column(DateTime)
    motor_state = Column(Boolean, default=False)

    def calculate_next_scheduled_time(self):
        current_time = datetime.now()
        deadline = self.session.session_start + \
            timedelta(days=self.session.turn_stage_start)

        while current_time < (self.session.session_start + timedelta(days=self.session.turn_stage_start) + timedelta(days=self.session.duration_turning_stage)):
            if current_time >= deadline:
                self.scheduled_time = deadline + \
                    timedelta(hours=self.session.turn_interval)

    def trigger_motor(self):
        current_time = datetime.now()
        if self.motor_state:
            return True
        if current_time >= (self.scheduled_time + timedelta(minutes=5)):
            self.motor_state = True
            return True
        if current_time >= (self.scheduled_time + timedelta(minutes=10)):
            self.calculate_next_scheduled_time()
            self.motor_state = False
            return False
