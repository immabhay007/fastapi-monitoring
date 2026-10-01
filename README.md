# FastAPI API Monitoring Dashboard Demo

A complete monitoring setup for a sample REST API built with FastAPI. It demonstrates API health tracking, performance monitoring, failure detection, alerting, and root cause analysis.

---

## 1. Overview

This project provides:

- A sample FastAPI service with success and failure endpoints
- Prometheus metrics scraping
- A Grafana dashboard with 10 panels
- Alertmanager with email notifications via MailHog
- Blackbox Exporter for uptime/health checks
- Four simulated failure scenarios with root cause analysis

---

## 2. Architecture

                    ┌─────────────────┐
                    │  FastAPI (8010) │
                    │  /metrics       │
                    └────────┬────────┘
                             │ scrape
                             ▼
┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│ Blackbox      │───▶│  Prometheus  │───▶│  Grafana     │
│ Exporter      │    │  (9090)      │    │  (3000)      │
│ (9115)        │    └──────┬───────┘    └──────────────┘
└───────────────┘           │
                       alerts│
                            ▼
                    ┌──────────────┐    ┌──────────────┐
                    │ Alertmanager │───▶│  MailHog     │
                    │  (9094)      │    │  (8025)      │
                    └──────────────┘    └──────────────┘

---

## 3. Tech Stack

| Component     | Role                          | Port |
|---------------|-------------------------------|------|
| FastAPI       | Sample REST API               | 8010 |
| Uvicorn       | ASGI server                   | 8000 (internal) |
| Prometheus    | Metrics collection + alerts   | 9090 |
| Grafana       | Dashboards                    | 3000 |
| Alertmanager  | Alert routing                 | 9094 |
| Blackbox Exp. | Health probing                | 9115 |
| MailHog       | Local SMTP + webmail UI       | 8025 / 1025 |
| Docker Compose| Orchestration                 | —    |

---

## 4. Project Structure

    new-age-fastapi-monitoring-demo/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── auth.py
    │   ├── metrics.py
    │   └── logging_config.py
    ├── monitoring/
    │   ├── prometheus.yml
    │   ├── alert.rules.yml
    │   ├── alertmanager.yml
    │   ├── blackbox.yml
    │   └── grafana/
    │       └── provisioning/
    │           └── datasources/
    │               └── prometheus.yml
    ├── scripts/
    │   └── test_failures.py
    ├── screenshots/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    └── README.md

---

## 5. API Endpoints

| Method | Endpoint              | Purpose                              | Expected |
|--------|-----------------------|--------------------------------------|----------|
| GET    | /health               | Health check                         | 200      |
| GET    | /users                | Sample users                         | 200      |
| GET    | /products             | Sample products                      | 200      |
| GET    | /simulate-error       | Raises HTTP 500                      | 500      |
| GET    | /simulate-timeout     | Delays 5 seconds                     | 200      |
| GET    | /simulate-rate-limit  | Returns HTTP 429                     | 429      |
| GET    | /secure               | Requires X-API-Key header            | 200 / 401|
| GET    | /metrics              | Prometheus metrics                   | 200      |

The /secure endpoint requires header `X-API-Key: secret-api-key-123`.

---

## 6. Setup Instructions

### Prerequisites
- Docker Desktop (with WSL 2 on Windows)
- Python 3.11+ (for local development, optional)
- Git (optional)

### Run the full stack

    git clone <your-repo-url>
    cd new-age-fastapi-monitoring-demo
    docker compose up -d

Wait ~30 seconds for all services to start. Confirm with:

    docker compose ps

All 6 services should show Up.

### Access URLs

| Service       | URL                            | Credentials      |
|---------------|--------------------------------|------------------|
| FastAPI docs  | http://localhost:8010/docs     | —                |
| FastAPI health| http://localhost:8010/health   | —                |
| Metrics       | http://localhost:8010/metrics  | —                |
| Prometheus    | http://localhost:9090          | —                |
| Grafana       | http://localhost:3000          | admin / admin    |
| Alertmanager  | http://localhost:9094          | —                |
| MailHog       | http://localhost:8025          | —                |

Note: FastAPI runs on port 8010 on the host to avoid conflicts with other local services. Internally it still listens on 8000.

### Run the FastAPI app locally (optional)

    python -m venv venv
    venv\Scripts\activate          # Windows
    pip install -r requirements.txt
    uvicorn app.main:app --reload

---

## 7. Monitoring Configuration

### Prometheus scrape jobs (monitoring/prometheus.yml)

- fastapi — scrapes http://fastapi:8000/metrics every 15s
- blackbox — probes http://fastapi:8000/health via Blackbox Exporter

### Metrics captured

| Metric                                          | Type      | Description                              |
|-------------------------------------------------|-----------|------------------------------------------|
| http_requests_total{method,path,status}         | Counter   | Total HTTP requests by status            |
| http_request_duration_seconds_bucket            | Histogram | Request latency distribution             |
| api_auth_failures_total{endpoint}               | Counter   | Authentication failures (401)            |
| api_rate_limit_hits_total{endpoint}             | Counter   | Rate limit hits (429)                    |
| api_server_errors_total{endpoint}               | Counter   | Server errors (500)                      |
| up{job="fastapi"}                               | Gauge     | Service availability (0=down, 1=up)      |
| probe_success{job="blackbox"}                   | Gauge     | Blackbox health probe success            |

### Grafana dashboard panels

1. API Status
2. API Uptime %
3. Total Requests (1h)
4. Failed Requests (5xx, 1h)
5. Average Response Time
6. Error Trends by Status Code
7. P95 Latency
8. Health Check (Blackbox)
9. Auth Failures (1h)
10. Rate Limit Hits (1h)

---

## 8. Alert Rules

Configured in monitoring/alert.rules.yml:

| Alert              | Condition                                                              | For  | Severity |
|--------------------|------------------------------------------------------------------------|------|----------|
| APIDown            | up{job="fastapi"} == 0                                                 | 1m   | critical |
| HighResponseTime   | P95 latency > 3 seconds                                                | 2m   | warning  |
| HTTP500Errors      | 500 errors occurring                                                   | 1m   | critical |
| HighFailureRate    | 5xx rate > 5% of all requests                                          | 2m   | warning  |
| HealthCheckFailed  | Blackbox probe_success == 0                                            | 1m   | critical |

### Notification channels

- Email via SMTP → MailHog (viewable at http://localhost:8025)
- Slack — placeholder webhook in alertmanager.yml; add your own URL to enable

---

## 9. Failure Testing & Root Cause Analysis

### How to run the failure tests

PowerShell (Windows):

    for ($i=0; $i -lt 60; $i++) {
      curl.exe -s http://localhost:8010/simulate-error | Out-Null
      curl.exe -s http://localhost:8010/simulate-rate-limit | Out-Null
      curl.exe -s -H "X-API-Key: wrong-key" http://localhost:8010/secure | Out-Null
      Start-Sleep -Seconds 2
    }

Python (cross-platform):

    python scripts/test_failures.py

---

### Scenario 1 — Invalid API Authentication

Trigger:

    curl -H "X-API-Key: wrong-key" http://localhost:8010/secure

Expected & observed:
- HTTP 401 Unauthorized
- api_auth_failures_total counter incremented
- Auth Failures panel shows non-zero value

Root cause: Client sent an invalid or missing API key. The endpoint rejects requests where X-API-Key != "secret-api-key-123".

Fix: Use the correct API key; rotate keys on the client side; add rate limiting to slow credential brute-forcing.

---

### Scenario 2 — API Timeout

Trigger:

    curl http://localhost:8010/simulate-timeout

Expected & observed:
- Response delayed 5 seconds
- Average Response Time and P95 Latency spikes
- HighResponseTime alert moves to Pending and can reach Firing

Root cause: Endpoint calls await asyncio.sleep(5) to simulate a downstream dependency that is slow or hanging.

Fix: Investigate downstream service latency, add timeouts and circuit breakers, optimize or cache slow queries.

---

### Scenario 3 — Server Error

Trigger:

    curl http://localhost:8010/simulate-error

Expected & observed:
- HTTP 500 Internal Server Error
- api_server_errors_total and 500 in http_requests_total incremented
- HTTP500Errors alert fires
- Email notification via Alertmanager → MailHog

Root cause: Endpoint raises HTTPException(500), simulating an unhandled server-side exception.

Fix: Inspect application logs (structured JSON with request ID), fix the exception, add defensive error handling, add unit tests.

---

### Scenario 4 — Rate Limit Exceeded

Trigger:

    curl http://localhost:8010/simulate-rate-limit

Expected & observed:
- HTTP 429 Too Many Requests
- api_rate_limit_hits_total incremented
- Rate Limit Hits panel shows non-zero value

Root cause: Client exceeded the allowed request quota.

Fix: Implement client-side backoff, respect Retry-After, tune rate limits if legitimate traffic is affected.

---

## 10. Screenshots

Stored in screenshots/:

- grafana-dashboard.png — full dashboard
- prometheus-alerts.png — firing alerts
- alertmanager.png — alert in Alertmanager
- mailhog-email.png — email notification proof

---

## 11. Limitations & Future Improvements

- Sample data is in-memory; a real deployment would use a database
- Alerts use email only by default; Slack webhook requires configuration
- No authentication on the monitoring stack; would need TLS + auth in production
- No Loki/Promtail for centralized logs; would add full log aggregation
- Single instance; production would use horizontal scaling and HA Prometheus

---

## 12. Deliverables Checklist

- [x] FastAPI source code (app/)
- [x] Monitoring configuration (monitoring/)
- [x] Grafana dashboard (10 panels)
- [x] Alert rules (5 alerts)
- [x] Alert notifications (email via MailHog, Slack webhook ready)
- [x] Failure simulation scripts (scripts/test_failures.py)
- [x] Root cause analysis documented above
- [x] Screenshots (screenshots/)
- [x] Technical documentation (this README)

---

## 13. Author

<Your Name>
<Your Email>