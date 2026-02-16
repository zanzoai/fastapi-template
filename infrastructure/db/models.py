from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    
    # Relationship to blogs
    blogs = relationship("Blog", back_populates="author")

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    author = relationship("User", back_populates="blogs")

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("zan_user.user_id"), nullable=False)
    task_title = Column(String, nullable=False)
    polished_task = Column(Text, nullable=False)
    location_address = Column(Text, nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    duration_hours = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    estimated_cost_pence = Column(Integer, nullable=False)
    assigned_zancrew_user_id = Column(Integer, nullable=True)
    short_title = Column(String, nullable=True)
    people_required = Column(Integer, nullable=False)
    imp_notes = Column(Text, nullable=True)
    actions = Column(String, nullable=False)
    tags = Column(String, nullable=False)
    bucket = Column(String, nullable=True)
    payment_mode = Column(String, nullable=False)
    payment_status = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    chat_room_id = Column(String, nullable=True)  # Denormalized; source of truth is chat_rooms.job_id
    status = Column(String(32), nullable=True, server_default="open")  # open | in_progress | closed
    pickup_adress = Column(Text, nullable=False)
    pickup_latitude = Column(String, nullable=False)
    pickup_longitude = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to zan_user
    zan_user = relationship("ZanUser", back_populates="jobs")
    # One chat room per job (created when job is assigned)
    chat_room = relationship("ChatRoom", back_populates="job", uselist=False, foreign_keys="ChatRoom.job_id")


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    is_read_only = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    job = relationship("Job", back_populates="chat_room")
    participants = relationship("ChatParticipant", back_populates="chat_room", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="chat_room", cascade="all, delete-orphan")


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    participant_type = Column(String(16), nullable=False)  # zan_user | zan_crew
    zan_user_id = Column(Integer, ForeignKey("zan_user.user_id", ondelete="CASCADE"), nullable=True)
    zancrew_id = Column(Integer, ForeignKey("zan_crew.zancrew_id", ondelete="CASCADE"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    chat_room = relationship("ChatRoom", back_populates="participants")
    zan_user = relationship("ZanUser", foreign_keys=[zan_user_id])
    zan_crew = relationship("ZanCrew", foreign_keys=[zancrew_id])
    message_reads = relationship("MessageRead", back_populates="participant", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(16), nullable=False)  # zan_user | zan_crew | system
    sender_zan_user_id = Column(Integer, nullable=True)
    sender_zancrew_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat_room = relationship("ChatRoom", back_populates="messages")
    reads = relationship("MessageRead", back_populates="message", cascade="all, delete-orphan")


class MessageRead(Base):
    __tablename__ = "message_reads"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(Integer, ForeignKey("chat_participants.id", ondelete="CASCADE"), nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("ChatMessage", back_populates="reads")
    participant = relationship("ChatParticipant", back_populates="message_reads")


class ZanUser(Base):
    __tablename__ = "zan_user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    is_zancrew = Column(String, nullable=True, default="false")
    zancrew_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to zan_crew
    zan_crew = relationship("ZanCrew", back_populates="zan_user", uselist=False)
    # Relationship to jobs
    jobs = relationship("Job", back_populates="zan_user")

class ZanCrew(Base):
    __tablename__ = "zan_crew"

    zancrew_id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
    pan_id = Column(String, nullable=True)
    adhar_id = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    martial_status = Column(String, nullable=True)
    zan_user_id = Column(Integer, ForeignKey("zan_user.user_id"), nullable=False)
    status = Column(String, nullable=True)
    radius_km = Column(Float, nullable=True)
    work_hours = Column(String, nullable=True)
    kyc_verified = Column(String, nullable=True)
    is_online = Column(String, nullable=True)
    payout_beneficiary_id = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    home_lat = Column(String, nullable=True)
    home_lng = Column(String, nullable=True)
    idfy_refs = Column(Text, nullable=True)
    pan_name = Column(String, nullable=True)
    pan_number_last4 = Column(String, nullable=True)
    aadhaar_verified = Column(String, nullable=True)
    aadhaar_last4 = Column(String, nullable=True)
    aadhar_city = Column(String, nullable=True)
    face_match_score = Column(Float, nullable=True)
    face_verified = Column(String, nullable=True)
    selfie_img_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to zan_user
    zan_user = relationship("ZanUser", back_populates="zan_crew")
