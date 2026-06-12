# ReguMind — Enterprise RAG Platform

Regulatory Intelligence and Verified AI Platform
Built with Python, FastAPI, LangChain, Qdrant, PostgreSQL, Docker, Groq LLM, Streamlit, Prometheus and Grafana

Author: Vishnu Priya D
LinkedIn: https://www.linkedin.com/in/vishnu-priya-duddukunta/
GitHub: https://github.com/vishnupriya-aiml
Email: vishnupriyadu@outlook.com

---

## What is ReguMind?

ReguMind is a production-grade Retrieval Augmented Generation (RAG) platform built from scratch that allows enterprises to upload regulatory documents and ask intelligent questions about them with AI-verified answers and hallucination detection.

This project demonstrates real-world enterprise AI engineering skills including RAG pipeline design, vector search, LLM integration, hallucination detection, monitoring, and full-stack deployment using Docker.

Think of it as ChatGPT for your private company documents, but with:
- Answers grounded only in YOUR documents, never from general AI knowledge
- Every sentence in the answer verified against source chunks
- Full permanent audit trail of every question asked in PostgreSQL
- Enterprise-grade monitoring with 6-panel Grafana dashboard
- Hybrid search combining vector similarity and BM25 keyword search
- One command Docker deployment of all 6 services

---

## Architecture Overview

User uploads documents and asks questions through the Streamlit dashboard.
The FastAPI backend handles all requests and orchestrates the pipeline.
Documents are chunked, embedded, and stored in Qdrant vector database.
Questions trigger hybrid search to retrieve the most relevant chunks.
Groq Llama 3.3 70B generates answers strictly from retrieved chunks.
Every sentence is verified for hallucination using a second LLM call.
All queries and answers are permanently saved to PostgreSQL.
Prometheus scrapes metrics every 15 seconds for Grafana dashboards.

Services running via Docker Compose:
1. regumind_api         FastAPI backend on port 8000
2. regumind_dashboard   Streamlit UI on port 8501
3. regumind_qdrant      Vector database on port 6333
4. regumind_postgres    Query history database on port 5432
5. regumind_prometheus  Metrics collection on port 9090
6. regumind_grafana     Monitoring dashboards on port 3000

---

## Key Features

Multi-Document Upload
Upload PDF, DOCX, and TXT files directly from the dashboard.
Each document is automatically processed through the full ingestion pipeline.

Hybrid Search Engine
Vector similarity search (70 percent weight) combined with BM25 keyword search (30 percent weight).
This approach outperforms pure vector search for regulatory documents with specific terminology.

AI Reasoning with Groq Llama 3.3 70B
Uses the free Groq API for fast inference.
The model is strictly prompted to answer ONLY from provided document chunks.
Every answer includes citations to the source documents used.

Sentence-Level Hallucination Detection
Every sentence in the AI answer is individually verified against the retrieved chunks.
A confidence score from 0 to 100 percent is calculated based on supported sentences.
Unsupported sentences are flagged and shown to the user.

Permanent Query History
PostgreSQL saves every question, answer, confidence score, hallucination status, sources, and response time.
Data survives Docker restarts and is accessible via the /history API endpoint.

Live Monitoring with Grafana
6-panel dashboard tracking:
  Panel 1: Total Questions Asked
  Panel 2: Average Confidence Score
  Panel 3: Documents Indexed in Qdrant
  Panel 4: Hallucinations Detected
  Panel 5: Document Chunks Ingested
  Panel 6: API Memory Usage in MB

Answer Caching
Repeated identical questions return instant cached responses.
Cache is maintained in Streamlit session state.

---

## Tech Stack

Backend
- Python 3.11
- FastAPI for REST API with async file upload support
- LangChain for LLM orchestration framework
- Groq API for free Llama 3.3 70B inference
- SQLAlchemy ORM for PostgreSQL
- psycopg2-binary for database connection
- uvicorn for ASGI server

Vector Database and Search
- Qdrant for vector storage and similarity search
- BAAI BGE-small-en-v1.5 local embedding model, 384 dimensions, completely free
- rank-bm25 for BM25 keyword search
- Custom hybrid search combining both with weighted scoring

Frontend Dashboard
- Streamlit with custom dark theme CSS
- 5 tabs: Ask ReguMind, Documents, Analytics, System Health, Chat History
- Real-time metrics display in the sidebar
- Word-by-word answer streaming effect
- File upload with automatic ingestion

Infrastructure and DevOps
- Docker Compose for 6-container orchestration
- PostgreSQL 15 for permanent data storage
- Prometheus for metrics collection with 15 second scrape interval
- Grafana for visualization dashboards

---

## Project Structure

regumind/
├── api/
│   └── main.py                FastAPI endpoints, startup, file upload handler
├── ingestion/
│   ├── document_loader.py     Loads PDF, DOCX, TXT with metadata extraction
│   └── pipeline.py            Master pipeline connecting all ingestion steps
├── processing/
│   ├── chunker.py             Text cleaning and 500-word chunking with 50-word overlap
│   ├── embedder.py            BGE embedding generation returning 384-dimensional vectors
│   └── database.py            PostgreSQL models for QueryHistory and DocumentHistory
├── retrieval/
│   ├── vector_store.py        Qdrant client, collection management, point counting
│   └── search_engine.py       Hybrid search combining vector and BM25 with weighting
├── ai_layer/
│   └── reasoning_engine.py    Groq Llama 3.3 70B with strict grounding system prompt
├── hallucination/
│   └── detector.py            Sentence splitting and per-sentence LLM verification
├── monitoring/
│   ├── metrics.py             Prometheus counters, histograms, and gauges definitions
│   └── prometheus.yml         Scrape config targeting regumind_api:8000/metrics
├── dashboard/
│   └── app.py                 Full Streamlit enterprise dashboard with 5 tabs
├── data/                      Document storage directory
├── config/
│   └── settings.py            Environment variable loading and app configuration
├── docker-compose.yml         6-service Docker Compose orchestration
├── Dockerfile                 Python 3.11 slim container with all dependencies
├── requirements.txt           All Python package dependencies with pinned versions
├── .env.example               Template showing required environment variables
└── README.md                  This file

---

## API Endpoints

GET  /           Returns welcome message and API version
GET  /health     System health check with document count and database status
GET  /stats      Platform statistics from both Qdrant and PostgreSQL
POST /ask        Main endpoint: ask a question and receive verified AI answer
POST /search     Semantic hybrid search returning ranked document chunks
POST /ingest     Upload file and index through full ingestion pipeline
GET  /history    Retrieve permanent query history from PostgreSQL
GET  /metrics    Prometheus metrics in text exposition format
GET  /docs       Auto-generated Swagger UI for interactive API testing

---

## How It Works Step by Step

Step 1: Document Ingestion
User uploads a PDF, DOCX, or TXT file through the dashboard Documents tab.
The file is received by the FastAPI /ingest endpoint as a multipart upload.
It is saved temporarily to /app/data/uploads/ inside the container.
The document loader extracts text and metadata including filename and file type.
The chunker cleans the text and splits it into 500-word chunks with 50-word overlap.
The embedder generates 384-dimensional vectors using BGE-small-en-v1.5 running locally.
Chunks with embeddings are stored in Qdrant under the regumind_documents collection.
A record is saved to PostgreSQL DocumentHistory table.
Prometheus counter regumind_documents_ingested_total is incremented.

Step 2: Question and Answer
User types a question in the Ask ReguMind tab and clicks the button.
The question is sent to the FastAPI /ask endpoint as a JSON POST request.
The question text is embedded using the same BGE model for consistency.
Qdrant performs cosine similarity search returning top K vectors.
BM25 keyword search runs on the same chunks in parallel.
Scores are combined: 70 percent vector score plus 30 percent BM25 score.
The top K ranked chunks are passed to the reasoning engine.

Step 3: AI Answer Generation
The question plus retrieved chunks are formatted into a structured prompt.
The system prompt strictly instructs: answer ONLY from the provided chunks.
Groq Llama 3.3 70B generates a grounded answer with source citations.
Temperature is configurable from the dashboard sidebar.

Step 4: Hallucination Verification
The answer is split into individual sentences using regex on punctuation.
Each sentence is sent to the LLM with the source chunks as context.
The LLM responds YES or NO for each sentence based on chunk support.
Confidence score equals supported sentences divided by total sentences.
Sentences scoring NO are flagged and shown to the user in the dashboard.

Step 5: Permanent Storage
The question, full answer, confidence score, hallucination boolean, source filenames,
chunk count, model name, and response time in seconds are saved to PostgreSQL.
This data persists across Docker restarts and is queryable via /history endpoint.

Step 6: Metrics Recording
Query count incremented on regumind_queries_total Prometheus counter.
Confidence score observed on regumind_confidence_score histogram.
If hallucination detected, regumind_hallucinations_detected_total incremented.
Response time observed on regumind_request_duration_seconds histogram.
Prometheus scrapes /metrics endpoint every 15 seconds.
Grafana reads from Prometheus and updates 6 dashboard panels in real time.

---

## Quick Start

Prerequisites
- Docker Desktop installed and running
- Free Groq API key from https://console.groq.com

Clone and run:

git clone https://github.com/vishnupriya-aiml/regumind.git
cd regumind
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
docker compose up --build

Access the platform:
Dashboard   http://localhost:8501
API         http://localhost:8000
API Docs    http://localhost:8000/docs
Qdrant      http://localhost:6333/dashboard
Prometheus  http://localhost:9090
Grafana     http://localhost:3000  login: admin / regumind123

---

## Skills Demonstrated

This project was built entirely from scratch and demonstrates:

Generative AI and RAG Engineering
- End-to-end RAG pipeline design and implementation
- Vector embeddings, semantic search, and retrieval strategies
- Hybrid search combining dense and sparse retrieval methods
- LLM prompt engineering with strict grounding constraints
- Hallucination detection using LLM-as-judge methodology
- Confidence scoring and uncertainty quantification

Backend and API Engineering
- REST API design with FastAPI following industry standards
- Async file upload handling with multipart form data
- SQLAlchemy ORM models with PostgreSQL relationships
- Prometheus metrics integration using counters, histograms, and gauges
- Docker multi-container networking and service dependencies

Data Engineering
- Document processing pipeline with multiple file format support
- Text chunking strategies with configurable size and overlap
- Embedding generation with local models for cost efficiency
- Persistent storage patterns for query history and audit trails

DevOps and Infrastructure
- Docker Compose orchestration of 6 interdependent services
- Container health checks and startup dependencies
- Service discovery using Docker internal DNS
- Monitoring stack setup with Prometheus and Grafana
- Volume management for data persistence across restarts

---

## About the Author

Vishnu Priya D is an AI/ML Engineer with 4 plus years of experience building Generative AI,
Predictive Models, and RAG systems across analytics and financial domains.

Experience includes:
- AI/ML Engineer at Uber USA building RAG pipelines on LangChain, FAISS, and transformer
  embeddings across 900K plus documents with 15K plus daily requests
- Data and ML Engineering at Airbnb India working with 10M plus booking records, predictive
  models, NLP pipelines, and AWS data infrastructure

Technical expertise spans Python, LangChain, LangGraph, FastAPI, PyTorch, Hugging Face,
vector search, hybrid search, hallucination detection, Docker, PostgreSQL, Prometheus,
Grafana, AWS, and Azure.

Currently seeking Senior AI/ML Engineer and Machine Learning Engineer opportunities.

LinkedIn: https://www.linkedin.com/in/vishnu-priya-duddukunta/
Email: vishnupriyadu@outlook.com
GitHub: https://github.com/vishnupriya-aiml

---

## License

MIT License
This project is open source. Feel free to reference it for learning and interview preparation.