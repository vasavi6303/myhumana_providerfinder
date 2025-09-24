# Multi-stage Dockerfile for production-ready FastAPI app using Gunicorn + Uvicorn workers
FROM python:3.11-slim as build
WORKDIR /tmp
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY src/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir /tmp/wheels -r /tmp/requirements.txt

FROM python:3.11-slim as runtime
RUN useradd -m -u 1000 appuser
WORKDIR /app
ENV PATH=/app/.local/bin:$PATH
COPY --from=build /tmp/wheels /wheels
COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache --no-index --upgrade -r /app/requirements.txt --find-links /wheels
# copy app
COPY src/app /app/app
# create non-root user and set permissions
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8080
# Use Gunicorn with Uvicorn workers for production
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--workers", "4", "--log-level", "info"]
