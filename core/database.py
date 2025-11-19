"""Database models and initialization for ShearwaterAICAD"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50))
    message_type = Column(String(50))
    content = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tier = Column(Integer)  # 1, 2, or 3


class Decision(Base):
    __tablename__ = 'decisions'

    id = Column(Integer, primary_key=True)
    decision_type = Column(String(100))
    agents_involved = Column(JSON)
    reasoning = Column(Text)
    outcome = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class CodeCommit(Base):
    __tablename__ = 'code_commits'

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50))
    file_path = Column(String(255))
    changes = Column(Text)
    review_status = Column(String(50))
    reviewer_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Reflection(Base):
    __tablename__ = 'reflections'

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50))
    reflection_type = Column(String(50))  # 'task', 'milestone', 'weekly'
    content = Column(Text)
    insights = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PerformanceMetric(Base):
    __tablename__ = 'performance_metrics'

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50))
    metric_name = Column(String(100))
    value = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)


def init_db(db_url="sqlite:///./shearwater_aicad.db"):
    """Initialize database with optional SQLite fallback"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
