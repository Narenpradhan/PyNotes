# 📝 Note-Taking API (FastAPI + MongoDB)

A simple, asynchronous REST API built with **FastAPI** and **MongoDB** using **Motor**. Designed to be lightweight and clean-ideal for practicing **Docker**, **Containerization**, and **Kubernetes** deployments!

---

## 📂 Project Structure

```
DevOps-Prac-v1/
├── app/
│   ├── __init__.py
│   ├── database.py       # MongoDB client configuration (motor)
│   ├── models.py         # Pydantic schemas (NoteCreate, NoteResponse, etc.)
│   ├── routes.py         # Endpoints for /notes (POST, GET, PUT, DELETE)
│   └── main.py           # FastAPI entrypoint, lifespan, & /health check
├── .dockerignore         # Docker ignore rules
├── Dockerfile            # Container definition (python:3.12-alpine3.24)
├── .env.example          # Sample environment variables
├── requirements.txt      # Python dependencies
└── README.md             # Documentation
```

---

## ⚙️ Environment Variables

The application reads configuration from environment variables (or a `.env` file):

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | `notes_db` | Name of the MongoDB database |
| `PORT` | `8000` | Port for the uvicorn server |

> 💡 **Tip for Docker & Kubernetes**: You can easily override `MONGO_URI` in Docker with `-e MONGO_URI=...` or in Kubernetes via `ConfigMap` / `Secret` environment variables.

---

## 🚀 Running Locally

### 1. Create and Activate Virtual Environment (Using `uv`)

```bash
# Create virtual environment with uv
uv venv

# Activate virtual environment:
# Windows (PowerShell / CMD)
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Using uv (fast)
uv pip install -r requirements.txt

# Or standard pip
pip install -r requirements.txt
```

### 3. Ensure MongoDB is Running

Run MongoDB with root credentials:
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo
```

The corresponding connection string in `.env` or `MONGO_URI` is:
```text
mongodb://admin:password@localhost:27017/?authSource=admin
```

### 4. Start the Application

```bash
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### 5. Run with Docker (Alternative)

```bash
# Build the Docker image
docker build -t notes-api .

# Run the container
docker run -d \
  --name notes-api \
  -p 8000:8000 \
  -e MONGO_URI="mongodb://admin:password@mongodb:27017/?authSource=admin" \
  notes-api
```

---

## 📌 API Endpoints

### Entity Schema (`Note`)
- `id` (*string*): 3-digit unique identifier (e.g., `"101"`, `"102"`)
- `title` (*string*): Title of the note
- `content` (*string*): Content/body of the note
- `created_at` (*datetime*): UTC creation timestamp
- `updated_at` (*datetime, optional*): UTC update timestamp

---

### Endpoints Overview

| Method | Endpoint | Description | Response Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | General health overview | `200 OK` |
| `GET` | `/health/live` (or `/livez`) | **Liveness Probe**: Verifies process is alive | `200 OK` |
| `GET` | `/health/ready` (or `/readyz`) | **Readiness Probe**: Verifies DB connectivity | `200 OK` / `503 Service Unavailable` |
| `GET` | `/health/startup` (or `/startupz`) | **Startup Probe**: Verifies initialization is done | `200 OK` / `503 Service Unavailable` |
| `POST` | `/notes` | Create a new note | `201 Created` |
| `GET` | `/notes` | List all notes | `200 OK` |
| `GET` | `/notes/{id}` | Fetch a note by 3-digit ID | `200 OK` (or `404`) |
| `PUT` | `/notes/{id}` | Update a note by 3-digit ID | `200 OK` (or `404`) |
| `DELETE`| `/notes/{id}` | Delete a note by 3-digit ID | `200 OK` (or `404`) |

---

### ☸️ Kubernetes Probe Configuration Example

When writing your Kubernetes `Deployment` manifest, you can configure the probes like this:

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

startupProbe:
  httpGet:
    path: /health/startup
    port: 8000
  failureThreshold: 30
  periodSeconds: 10
```

---

### 🧪 Sample `curl` Requests

#### 1. Probes & Health Checks
```bash
# Liveness probe
curl -X GET "http://localhost:8000/health/live"

# Readiness probe
curl -X GET "http://localhost:8000/health/ready"

# Startup probe
curl -X GET "http://localhost:8000/health/startup"
```

#### 2. Create a Note (`POST /notes`)
```bash
curl -X POST "http://localhost:8000/notes" \
     -H "Content-Type: application/json" \
     -d '{"title": "DevOps Practice", "content": "Practice Dockerizing FastAPI and deploying to K8s!"}'
```

**Response (`201 Created`):**
```json
{
  "message": "Note created successfully",
  "data": {
    "id": "101",
    "title": "DevOps Practice",
    "content": "Practice Dockerizing FastAPI and deploying to K8s!",
    "created_at": "2026-09-01T10:00:00.000Z",
    "updated_at": null
  }
}
```

#### 3. Get All Notes (`GET /notes`)
```bash
curl -X GET "http://localhost:8000/notes"
```

#### 4. Get Note by ID (`GET /notes/101`)
```bash
curl -X GET "http://localhost:8000/notes/101"
```

#### 5. Update a Note (`PUT /notes/101`)
```bash
curl -X PUT "http://localhost:8000/notes/101" \
     -H "Content-Type: application/json" \
     -d '{"title": "Updated Title", "content": "Updated content details"}'
```
**Response (`200 OK`):**
```json
{
  "message": "Note with ID '101' updated successfully",
  "data": {
    "id": "101",
    "title": "Updated Title",
    "content": "Updated content details",
    "created_at": "2026-09-01T10:00:00.000Z",
    "updated_at": "2026-09-01T10:05:00.000Z"
  }
}
```

#### 6. Delete a Note (`DELETE /notes/101`)
```bash
curl -X DELETE "http://localhost:8000/notes/101"
```
**Response (`200 OK`):**
```json
{
  "message": "Note with ID '101' deleted successfully",
  "id": "101"
}
```
