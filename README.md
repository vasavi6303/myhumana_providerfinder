# MyHumana Provider Finder - Production-ready Demo Repo

This repo contains a production-ready reference implementation of the Provider Finder microservice
(FastAPI) and the associated CI/CD, infrastructure, Helm chart, monitoring, and security skeletons.

**Contents**
- `src/` — FastAPI application, Healthpilot client, models, tests.
- `Dockerfile` — multi-stage production build (non-root user + Gunicorn + Uvicorn workers).
- `helm-chart/` — Helm chart to deploy onto EKS.
- `infra/terraform/` — Terraform skeleton to create ECR + EKS (use modules for production).
- `.github/workflows/` — CI (tests, lint, scans) and CD (build/push to ECR + helm deploy).
- `cicd/jenkins/Jenkinsfile` — optional Jenkins pipeline.
- `observability/` — Prometheus & Grafana skeletons and instrumentation example.

**How to use (quick)**
1. Build & run locally:
   ```bash
   docker build -t providerfinder:local .
   docker run -e MOCK_HP=true -p 8080:8080 providerfinder:local
   ```
2. Run tests:
   ```bash
   pip install -r src/requirements.txt
   pytest -q
   ```
3. For production: create ECR, EKS via `infra/terraform`, set up GitHub secrets, and push to `main` branch.
