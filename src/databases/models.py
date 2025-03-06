from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .db import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    user_name = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, nullable=False)
    last_activity = Column(DateTime, nullable=False)
    summary = Column(String, nullable=False)
    needs_date = Column(Boolean, nullable=False)
    needs_location = Column(Boolean, nullable=False)
    needs_reservation = Column(Boolean, nullable=False)
    reminder_sent = Column(Boolean, default=False)
