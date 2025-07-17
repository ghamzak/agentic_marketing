"""
SQLAlchemy ORM models for Agentic Marketing system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Business(Base):    
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    contact_email = Column(String(256))
    contact_phone = Column(String(64))
    description = Column(Text)
    website = Column(String(256))
    region = Column(String(128))
    industry = Column(String(128))
    # Removed social_media. Add Tavily agent fields:
    yelp_url = Column(String(256))
    yelp_description = Column(Text)
    trends = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    leads = relationship("Lead", back_populates="business")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    score = Column(Float, nullable=False)
    status = Column(String(32), default="new")  # new, selected, contacted, etc.
    enriched_data = Column(JSON)  # trend columns, recent promotions, etc.
    predicted_ROI = Column(Float)
    predicted_probability = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    business = relationship("Business", back_populates="leads")
    personas = relationship("Persona", back_populates="lead")
    outreach_contents = relationship("OutreachContent", back_populates="lead")

class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    persona_json = Column(JSON)  # LLM-generated persona
    created_at = Column(DateTime, default=datetime.utcnow)
    lead = relationship("Lead", back_populates="personas")

class OutreachContent(Base):
    __tablename__ = "outreach_contents"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    channel = Column(String(32))  # email, instagram, tiktok, telegram
    content = Column(Text)
    approved = Column(Boolean, default=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    lead = relationship("Lead", back_populates="outreach_contents")

class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64))
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
