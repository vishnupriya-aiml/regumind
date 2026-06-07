# api/main.py
import time
import os
import sys
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import uvicorn

from retrieval.vector_store import create_collection, get_collection_info
from retrieval.search_engine import hybrid_search
from ingestion.pipeline import run_pipeline, ingest_document
from ai_layer.reasoning_engine import get_answer
from hallucination.detector import check_hallucination
from monitoring.metrics import (
    record_query, update_documents_indexed,
    record_hallucination, record_documents_ingested,
    get_metrics_data
)
from processing.database import (
    create_tables, save_query, save_document,
    get_query_history, get_stats
)

app = FastAPI(
    title="ReguMind API",
    description="Enterprise Regulatory Intelligence & Verified RAG Platform",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
        print("Database tables initialized successfully!")
    except Exception as e:
        print(f"Database initialization warning: {e}")


# ── REQUEST MODELS ──
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    temperature: Optional[float] = 0.1
    check_hallucination: Optional[bool] = True


# ── ENDPOINTS ──

@app.get("/")
def root():
    return {
        "message": "Welcome to ReguMind API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    try:
        create_collection()
        info = get_collection_info()
        total = info['total_vectors'] or 0
        update_documents_indexed(total)
        return {
            "status": "healthy",
            "vector_database": "connected",
            "total_documents_indexed": total,
            "collection": info['name']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_document_upload(file: UploadFile = File(...)):
    """
    Accepts a file upload directly from the dashboard.
    Saves it temporarily, ingests it, then cleans up.
    """
    try:
        start_time = time.time()

        # Save uploaded file temporarily
        upload_dir = "/app/data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        file_size = len(content)

        # Run ingestion pipeline
        result = run_pipeline(file_path)
        duration = time.time() - start_time

        if result['success']:
            record_documents_ingested(result['chunks_stored'])
            save_document(
                filename=file.filename,
                file_type=file.filename.split('.')[-1],
                chunks_created=result['chunks_stored'],
                file_size_bytes=file_size
            )
            return {
                "status": "success",
                "message": f"Document ingested successfully",
                "filename": file.filename,
                "chunks_stored": result['chunks_stored'],
                "chunks_created": result['chunks_stored'],
                "duration_seconds": round(duration, 2)
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Ingestion failed')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
def search_documents(request: SearchRequest):
    try:
        results = hybrid_search(request.query, top_k=request.top_k)
        return {
            "query": request.query,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask_question(request: AskRequest):
    try:
        start_time = time.time()

        chunks = hybrid_search(request.question, top_k=request.top_k)

        if not chunks:
            return {
                "question": request.question,
                "answer": "No relevant information found in the knowledge base.",
                "confidence_score": 0.0,
                "sources": [],
                "hallucination_detected": False,
                "chunks_retrieved": 0,
                "model_used": "none",
                "response_time_seconds": 0
            }

        answer = get_answer(
            question=request.question,
            context_chunks=chunks,
            temperature=request.temperature
        )

        hallucination_result = {
            "hallucination_detected": False,
            "confidence_score": 1.0
        }
        if request.check_hallucination:
            hallucination_result = check_hallucination(answer, chunks)

        duration = time.time() - start_time

        record_query(
            confidence=hallucination_result.get('confidence_score', 1.0),
            hallucination=hallucination_result.get('hallucination_detected', False),
            response_time=duration
        )

        if hallucination_result.get('hallucination_detected'):
            record_hallucination()

        sources = [c.get('source_filename', '') for c in chunks[:3]]

        save_query(
            question=request.question,
            answer=answer,
            confidence_score=hallucination_result.get('confidence_score', 1.0),
            hallucination_detected=hallucination_result.get(
                'hallucination_detected', False),
            sources_used=str(sources),
            chunks_retrieved=len(chunks),
            model_used="llama-3.3-70b-versatile",
            response_time=duration
        )

        return {
            "question": request.question,
            "answer": answer,
            "confidence_score": hallucination_result.get('confidence_score', 1.0),
            "hallucination_detected": hallucination_result.get(
                'hallucination_detected', False),
            "sources": sources,
            "chunks_retrieved": len(chunks),
            "model_used": "llama-3.3-70b-versatile",
            "response_time_seconds": round(duration, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_statistics():
    try:
        info = get_collection_info()
        total_vectors = info.get('total_vectors', 0)
        db_stats = get_stats()
        return {
            "total_documents_indexed": total_vectors,
            "total_queries_from_db": db_stats['total_queries'],
            "avg_confidence_from_db": db_stats['avg_confidence'],
            "total_documents_ingested": db_stats['total_documents'],
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "ai_model": "llama-3.3-70b-versatile"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_history(limit: int = 20):
    try:
        records = get_query_history(limit=limit)
        history = []
        for r in records:
            history.append({
                "id": r.id,
                "question": r.question,
                "answer": r.answer[:200] + "..." if len(r.answer) > 200 else r.answer,
                "confidence_score": r.confidence_score,
                "hallucination_detected": bool(r.hallucination_detected),
                "response_time": r.response_time_seconds,
                "created_at": str(r.created_at)
            })
        return {"history": history, "total": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    return get_metrics_data()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)