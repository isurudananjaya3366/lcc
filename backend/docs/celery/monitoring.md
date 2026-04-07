# Celery Monitoring — Flower

> LankaCommerce Cloud — Celery task monitoring with Flower.

## Overview

[Flower](https://flower.readthedocs.io/) is the de-facto real-time web
UI for monitoring Celery clusters. It provides:

- **Task progress & history** — view running, completed, failed, and
  retried tasks with full argument / result detail.
- **Worker status** — online/offline, active task count, CPU, memory.
- **Queue lengths** — depth of each broker queue
  (`high_priority`, `default`, `low_priority`).
- **Rate limiting** — throttle tasks per worker / per task type.
- **Broker connectivity** — monitor Redis connection health.

---

## Quick-start (local, no Docker)

```bash
# Inside the backend virtualenv
pip install flower

# Start Flower against the project Celery app
celery -A config.celery flower \
    --port=5555 \
    --broker=redis://localhost:6379/0
```

Then open <http://localhost:5555>.

---

## Docker Compose Setup

Add the following service to `docker-compose.yml` (or the override file):

```yaml
  flower:
    image: mher/flower:2.0
    container_name: lcc-flower
    command: >
      celery
        --broker=redis://redis:6379/0
        flower
        --port=5555
        --persistent=True
        --db=/data/flower.db
        --basic-auth=${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-changeme}
    ports:
      - "5555:5555"
    volumes:
      - flower_data:/data
    depends_on:
      - redis
      - backend
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    networks:
      - lcc-network
    restart: unless-stopped

volumes:
  flower_data:
```

### Environment Variables

| Variable            | Default    | Description              |
| ------------------- | ---------- | ------------------------ |
| `FLOWER_USER`       | `admin`    | HTTP basic-auth username |
| `FLOWER_PASSWORD`   | `changeme` | HTTP basic-auth password |
| `CELERY_BROKER_URL` | (required) | Redis URL for the broker |

> **Security**: Always change the default password in production. In
> staging / production, put Flower behind an HTTPS reverse proxy and
> restrict access via VPN or IP allowlist.

---

## Production Considerations

### Authentication

Flower supports multiple auth backends:

```bash
# Google OAuth (flower >= 2.0)
celery -A config.celery flower \
    --auth=.*@lankacommerce\.com \
    --oauth2_key=<client_id> \
    --oauth2_secret=<client_secret> \
    --oauth2_redirect_uri=https://flower.example.com/login
```

### Persistence

Enable `--persistent=True --db=/data/flower.db` to survive restarts.

### Prometheus Integration

Flower exposes a `/metrics` endpoint compatible with Prometheus. Add a
scrape target:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: flower
    static_configs:
      - targets: ["flower:5555"]
```

### Alerting

Configure alerts in Prometheus / Grafana for:

- `celery_task_failed_total` increasing above threshold
- Queue depth (`celery_queue_length`) exceeding capacity
- Worker count dropping below minimum

---

## Useful Flower API Endpoints

| Endpoint                     | Method | Description           |
| ---------------------------- | ------ | --------------------- |
| `/api/workers`               | GET    | List all workers      |
| `/api/tasks`                 | GET    | List recent tasks     |
| `/api/task/info/<task-id>`   | GET    | Task detail           |
| `/api/task/revoke/<task-id>` | POST   | Revoke a running task |
| `/api/queues/length`         | GET    | Current queue lengths |

---

## CLI Reference

```bash
# Start flower with all options
celery -A config.celery flower \
    --port=5555 \
    --broker=redis://redis:6379/0 \
    --persistent=True \
    --db=/data/flower.db \
    --basic-auth=admin:secret \
    --max-tasks=10000 \
    --purge-offline-workers=60
```

---

## Troubleshooting

| Symptom                     | Fix                                            |
| --------------------------- | ---------------------------------------------- |
| "No workers found"          | Ensure at least one `celery worker` is running |
| Tasks not appearing         | Verify `CELERY_BROKER_URL` matches the worker  |
| High memory usage           | Reduce `--max-tasks` (default 10 000)          |
| Dashboard loads but no data | Check Redis connectivity from Flower container |
