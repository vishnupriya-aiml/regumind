# processing/database.py
# This file handles all PostgreSQL database operations
# It permanently saves every question and answer ReguMind processes

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:regumind123@localhost:5432/regumind"
)

# Create database engine
engine = create_engine(DATABASE_URL)

# Base class for all database models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── DATABASE MODELS ──
# A model defines the structure of a database table
# Think of it like defining columns in an Excel spreadsheet

class QueryHistory(Base):
    """
    Stores every question asked to ReguMind permanently.
    Even after restart all history is preserved.
    """
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0)
    hallucination_detected = Column(Integer, default=0)
    sources_used = Column(String(500), default="")
    chunks_retrieved = Column(Integer, default=0)
    model_used = Column(String(100), default="")
    response_time_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentHistory(Base):
    """
    Stores every document that has been ingested into ReguMind.
    Keeps a permanent record of the knowledge base.
    """
    __tablename__ = "document_history"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), default="")
    chunks_created = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    ingested_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """
    Creates all database tables if they do not exist yet.
    Safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def get_db():
    """
    Returns a database session.
    Always close the session after use.
    """
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def save_query(question, answer, confidence_score=0.0,
               hallucination_detected=False, sources_used="",
               chunks_retrieved=0, model_used="", response_time=0.0):
    """
    Saves a question and answer to the database permanently.
    Called every time someone asks ReguMind a question.
    """
    db = SessionLocal()
    try:
        query_record = QueryHistory(
            question=question,
            answer=answer,
            confidence_score=confidence_score,
            hallucination_detected=1 if hallucination_detected else 0,
            sources_used=str(sources_used)[:500],
            chunks_retrieved=chunks_retrieved,
            model_used=model_used,
            response_time_seconds=response_time
        )
        db.add(query_record)
        db.commit()
        print(f"Query saved to database: {question[:50]}...")
        return query_record.id
    except Exception as e:
        db.rollback()
        print(f"Failed to save query: {e}")
        return None
    finally:
        db.close()


def save_document(filename, file_type="", chunks_created=0, file_size_bytes=0):
    """
    Saves a document ingestion record to the database.
    Called every time a document is ingested.
    """
    db = SessionLocal()
    try:
        doc_record = DocumentHistory(
            filename=filename,
            file_type=file_type,
            chunks_created=chunks_created,
            file_size_bytes=file_size_bytes
        )
        db.add(doc_record)
        db.commit()
        print(f"Document saved to database: {filename}")
        return doc_record.id
    except Exception as e:
        db.rollback()
        print(f"Failed to save document: {e}")
        return None
    finally:
        db.close()


def get_query_history(limit=50):
    """
    Retrieves the most recent queries from the database.
    Returns them newest first.
    """
    db = SessionLocal()
    try:
        records = db.query(QueryHistory)\
                    .order_by(QueryHistory.created_at.desc())\
                    .limit(limit)\
                    .all()
        return records
    except Exception as e:
        print(f"Failed to get history: {e}")
        return []
    finally:
        db.close()


def get_stats():
    """
    Returns overall statistics from the database.
    """
    db = SessionLocal()
    try:
        total_queries = db.query(QueryHistory).count()
        avg_confidence = db.query(QueryHistory).all()
        if avg_confidence:
            avg = sum(q.confidence_score for q in avg_confidence) / len(avg_confidence)
        else:
            avg = 0.0
        total_docs = db.query(DocumentHistory).count()
        return {
            "total_queries": total_queries,
            "avg_confidence": round(avg, 4),
            "total_documents": total_docs
        }
    except Exception as e:
        print(f"Failed to get stats: {e}")
        return {"total_queries": 0, "avg_confidence": 0.0, "total_documents": 0}
    finally:
        db.close()


if __name__ == "__main__":
    print("Testing database connection...")
    try:
        create_tables()
        print("Database connection successful!")
        stats = get_stats()
        print(f"Current stats: {stats}")
    except Exception as e:
        print(f"Database connection failed: {e}")