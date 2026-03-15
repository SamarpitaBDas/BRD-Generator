# BRD Generator – Setup Guide

> Django · ML · Amazon Nova 2 Lite via Bedrock

---

## What's new

- Amazon Nova 2 Lite integration via Amazon Bedrock Runtime
- New endpoint: `POST /api/generate-brd/`
- `nova_brd_generator.py` added to `ml_models/`
- `boto3` added to `requirements.txt`

---

## Prerequisites

Make sure you have:

- Python **3.8+**
- pip
- Redis _(optional, for Celery)_
- AWS account with Bedrock access enabled
- IAM user or role with `bedrock:InvokeModel` permission

```bash
python --version
pip --version
```

### Enable Nova 2 Lite in AWS

1. Open the AWS Console → **Amazon Bedrock**
2. Go to **Model access** in the left sidebar
3. Request access to `amazon.nova-2-lite-v1:0` under Amazon models
4. Wait for approval (usually instant for Nova models)

**Required IAM permission:**

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "arn:aws:bedrock:*::foundation-model/amazon.nova-2-lite-v1:0"
}
```

---

## Installation

### Option A — Automated (Linux/Mac)

```bash
chmod +x setup.sh
./setup.sh
```

### Option B — Automated (Windows)

```cmd
setup.bat
```

### Option C — Manual Setup

#### Step 1 — Create virtual environment

```bash
python -m venv venv
```

#### Step 2 — Activate

**Linux / Mac**

```bash
source venv/bin/activate
```

**Windows**

```cmd
venv\Scripts\activate
```

#### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
pip install -r frontend_requirements.txt
```

> First installation may take time — ML models + torch download ~2–3 GB.
> `boto3` and `botocore` are included in `requirements.txt` for Bedrock support.

#### Step 4 — Setup database

```bash
cd backend
python manage.py migrate
```

#### Step 5 — Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:

```env
# AWS Bedrock credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# Optional: only needed for temporary credentials
# AWS_SESSION_TOKEN=your_session_token_here
```

> **Credential resolution order (boto3 standard chain):**
> 1. Environment variables: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
> 2. `~/.aws/credentials` file (`aws configure`)
> 3. IAM instance or task role (EC2, ECS, Lambda)

---

## Running the Application

### Terminal 1 — Start Django backend

```bash
cd backend
python manage.py runserver
# Backend running at: http://localhost:8000
```

### Terminal 2 — Start frontend (Streamlit)

```bash
python frontend/main.py
```

---

## Using the Nova 2 Lite Endpoint

Once the backend is running, generate a BRD by sending a POST request to:

```
POST http://localhost:8000/api/generate-brd/
```

### Request body

```json
{
  "product_name":      "SmartInventory",
  "problem_statement": "Warehouses lack real-time stock visibility.",
  "target_users":      "Warehouse managers and operations staff",
  "key_features":      "Real-time tracking, low-stock alerts, reporting"
}
```

### Response

```json
{
  "brd": "1. Introduction\n\nPurpose: ...\n\n2. Scope ..."
}
```

### Example with curl

```bash
curl -X POST http://localhost:8000/api/generate-brd/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "SmartInventory",
    "problem_statement": "Warehouses lack real-time stock visibility.",
    "target_users": "Warehouse managers",
    "key_features": "Tracking, alerts, dashboards"
  }'
```

### Generated BRD sections

- **Introduction** — purpose, background, document scope
- **Scope** — in-scope features, out-of-scope items, assumptions
- **Stakeholders** — roles and interests
- **Functional Requirements** — numbered FR-001, FR-002, ...
- **Non-Functional Requirements** — numbered NFR-001, NFR-002, ...
- **Success Metrics** — KPIs and acceptance criteria

---

## Optional: Background Processing (Celery)

### Terminal 3 — Start Redis

```bash
redis-server
```

### Terminal 4 — Start Celery worker

```bash
cd backend
celery -A brd_backend worker --loglevel=info
```

---

## Common Commands

```bash
# Create admin user
python manage.py createsuperuser

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Run on a different port
python manage.py runserver 8001
```

### AWS CLI credential setup

```bash
# Configure credentials interactively
aws configure

# Verify credentials are working
aws sts get-caller-identity

# Check Bedrock model access
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'nova')].[modelId,modelLifecycleStatus]"
```

---

## First Run Notes

- ML models download on first execution (~2–3 GB) — startup may take 5–10 minutes
- Subsequent runs are much faster (cached locally)
- Nova 2 Lite calls are made live to AWS Bedrock — ensure credentials are valid and the model is enabled in your AWS region before starting

---

## Project Structure

```
brd_generator_project/
├── backend/
│   ├── manage.py
│   ├── brd_backend/
│   ├── api/
│   │   ├── views.py          ← nova_generate_brd endpoint added here
│   │   └── urls.py           ← /api/generate-brd/ registered here
│   ├── ml_models/
│   │   └── nova_brd_generator.py   ← NEW: Bedrock + Nova integration
│   └── integrations/
├── frontend/
│   └── main.py
├── .env                      ← AWS credentials go here
├── requirements.txt          ← boto3 added
└── frontend_requirements.txt
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| Port already in use | `python manage.py runserver 8001` |
| Module not found | `pip install -r requirements.txt` |
| Database locked | Stop all Django processes and restart |
| `NoCredentialsError` | Set `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in `.env` or run `aws configure` |
| `AccessDeniedException` | Add `bedrock:InvokeModel` to your IAM policy and enable Nova 2 Lite in the Bedrock console |
| `ResourceNotFoundException` | Check `AWS_DEFAULT_REGION=us-east-1` and that model access is approved |
| `boto3` not found | `pip install boto3 botocore` (already in `requirements.txt`) |

---

_Icon assets from [remixicon.com](https://remixicon.com/) · BRD Generator · Amazon Nova 2 Lite via Bedrock_