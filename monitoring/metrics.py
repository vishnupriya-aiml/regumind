# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
import time

# ── COUNTERS ──
REQUEST_COUNT = Counter(
    'regumind_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

QUERY_COUNT = Counter(
    'regumind_queries_total',
    'Total number of questions asked to ReguMind'
)

DOCUMENTS_INGESTED = Counter(
    'regumind_documents_ingested_total',
    'Total number of documents ingested'
)

CACHE_HITS = Counter(
    'regumind_cache_hits_total',
    'Total number of cache hits'
)

HALLUCINATIONS_DETECTED = Counter(
    'regumind_hallucinations_detected_total',
    'Total number of responses with hallucinations flagged'
)

# ── HISTOGRAMS ──
REQUEST_DURATION = Histogram(
    'regumind_request_duration_seconds',
    'Time spent processing API requests',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

SEARCH_DURATION = Histogram(
    'regumind_search_duration_seconds',
    'Time spent on hybrid search',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

AI_DURATION = Histogram(
    'regumind_ai_duration_seconds',
    'Time spent generating AI answers',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

CONFIDENCE_SCORE = Histogram(
    'regumind_confidence_score',
    'Distribution of confidence scores',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# ── GAUGES ──
DOCUMENTS_INDEXED = Gauge(
    'regumind_documents_indexed',
    'Current number of document vectors in database'
)

CACHE_SIZE = Gauge(
    'regumind_cache_size',
    'Current number of queries in cache'
)


def record_request(method, endpoint, status, duration):
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=str(status)
    ).inc()
    REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)


def record_query(confidence=1.0, hallucination=False, response_time=0.0):
    """Called by API after every question — matches api/main.py signature."""
    QUERY_COUNT.inc()
    CONFIDENCE_SCORE.observe(confidence)
    if hallucination:
        HALLUCINATIONS_DETECTED.inc()


def record_hallucination():
    HALLUCINATIONS_DETECTED.inc()


def record_documents_ingested(count=1):
    DOCUMENTS_INGESTED.inc(count)


def record_cache_hit():
    CACHE_HITS.inc()


def update_documents_indexed(count):
    DOCUMENTS_INDEXED.set(count)


def update_cache_size(size):
    CACHE_SIZE.set(size)


def get_metrics_data():
    from fastapi.responses import Response
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    print("Metrics module ready!")