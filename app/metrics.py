from prometheus_client import Counter, Histogram

# Custom metrics
AUTH_FAILURES = Counter(
    'api_auth_failures_total',
    'Total number of authentication failures',
    ['endpoint']
)

RATE_LIMIT_HITS = Counter(
    'api_rate_limit_hits_total',
    'Total number of rate limit hits',
    ['endpoint']
)

SERVER_ERRORS = Counter(
    'api_server_errors_total',
    'Total number of server errors',
    ['endpoint']
)

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0)
)