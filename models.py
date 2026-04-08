from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Date, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversations = relationship("Conversation", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    memory = relationship("UserMemory", back_populates="user")
    trips = relationship("Trip", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(200))
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    user_query = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    budget = Column(Integer)
    travel_style = Column(String(100))
    preferred_location = Column(String(150))
    hotel_type = Column(String(100))
    preferred_transport = Column(String(100))
    updated_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="preferences")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    origin = Column(String(150))
    destination = Column(String(150), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="trips")
    itineraries = relationship("Itinerary", back_populates="trip")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"))
    day = Column(Integer)
    plan = Column(Text)

    trip = relationship("Trip", back_populates="itineraries")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(200), nullable=False)
    document_category = Column(String(100), nullable=False)
    source_type = Column(String(100))
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    faiss_doc_key = Column(String(100), unique=True, nullable=False)
    is_active = Column(String(10), default="TRUE")
    created_at = Column(TIMESTAMP, server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    chunk = Column(Text, nullable=False)
    faiss_vector_id = Column(Integer)
    metadata_json = Column(JSON)

    document = relationship("Document", back_populates="chunks")


class RoleAccessPolicy(Base):
    __tablename__ = "role_access_policies"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    access_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())