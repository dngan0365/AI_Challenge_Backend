

## Project Structure and Key Files

```text
your_project/
│
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── core/                  # Core configs, settings, and utilities
│   │   ├── config.py
│   │   └── adk.py             # ADK integration helpers/utilities
│   ├── db/                    # Database connection and session management
│   │   ├── database.py
│   │   └── session.py
│   ├── models/                # Database models (e.g., Video, User)
│   ├── schemas/               # Pydantic schemas for request/response
│   ├── crud/                  # CRUD operations for models
│   ├── ai/                    # AI agent logic, model loading, inference
│   │   ├── agent.py
│   │   └── video_retrieval.py # Video retrieval logic using AI
│   ├── cloud/                 # Google Cloud integration (storage, pubsub, etc.)
│   │   ├── storage.py         # Google Cloud Storage helpers
│   │   ├── pubsub.py          # Pub/Sub integration
│   │   └── vision.py          # (Optional) Vision API helpers
│   ├── services/              # Business logic, orchestration
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/     # API endpoints (e.g., videos.py, search.py)
│   │       ├── deps.py        # Dependencies for endpoints
│   │       └── main.py        # API router
│   └── utils/                 # Utility functions (e.g., file handling)
│
├── tests/                     # Unit and integration tests
├── migrations/                # DB migration scripts (e.g., Alembic)
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
```


### Description of Key Directories and Files

- **your_project/**: The root directory of your project.
- **app/**: Contains the main application code.
- **main.py**: The entry point of your FastAPI application, where the FastAPI instance is created and routers are included.
- **core/**: Core application configurations, settings, and ADK integration.
	- **config.py**: Manages environment variables and application settings.
	- **adk.py**: Handles ADK (AI Development Kit) integration and helpers.
- **db/**: Database connection and session management.
	- **database.py**: Defines the database connection and engine.
	- **session.py**: Manages database sessions.
- **models/**: Database models (e.g., Video, User).
- **schemas/**: Pydantic schemas for data validation and serialization/deserialization of request and response bodies.
- **crud/**: Implements Create, Read, Update, Delete (CRUD) operations for interacting with the database models.
- **ai/**: AI agent logic, model loading, and video retrieval using AI.
	- **agent.py**: AI agent orchestration.
	- **video_retrieval.py**: Video retrieval logic using AI models.
- **cloud/**: Google Cloud service integrations.
	- **storage.py**: Google Cloud Storage helpers.
	- **pubsub.py**: Google Pub/Sub integration.
	- **vision.py**: (Optional) Google Vision API helpers.
- **services/**: Business logic and orchestration, combining AI, CRUD, and cloud services.
- **api/**: Organizes your API endpoints, often versioned.
	- **v1/**: Directory for API version 1.
		- **endpoints/**: Contains individual endpoint modules (e.g., videos.py for video endpoints, search.py for search endpoints).
		- **deps.py**: Defines common dependencies used across multiple endpoints.
		- **main.py**: Includes the APIRouter instances from different endpoint modules.
- **utils/**: Utility functions (e.g., file handling, video processing).
- **tests/**: Unit and integration tests for your application.
- **migrations/**: If using a database migration tool like Alembic, this directory holds migration scripts.
- **.env**: Stores environment-specific variables.
- **requirements.txt**: Lists project dependencies.
- **README.md**: Provides project documentation.
# FastAPI Backend Deployment Guide



## Introduction

This guide explains how to deploy a FastAPI application to Google Cloud Run.

## Local Setup (for testing on your machine)

1. Install Python 3.11

2. (Recommended) Create and activate a virtual environment:

	```bash
	python -m venv venv
	# On Windows:
	venv\Scripts\activate
	# On macOS/Linux:
	source venv/bin/activate
	```

3. Install required packages:

	```bash
	pip install -r requirements.txt
	```

4. Run the application:

	```bash
	uvicorn main:app --host 0.0.0.0 --port 8080
	```



## Package FastAPI with Docker

Create a `Dockerfile` with the following content:

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```


## Build and Push Image to Google Artifact Registry

1. Log in to Google Cloud:

	```bash
	gcloud auth login
	gcloud config set project PROJECT_ID
	```

2. Build and push the image:

	```bash
	gcloud builds submit --tag gcr.io/PROJECT_ID/fastapi-backend
	```



## Deploy to Google Cloud Run

```bash
gcloud run deploy fastapi-backend \
	--image gcr.io/PROJECT_ID/fastapi-backend \
	--region asia-southeast1 \
	--platform managed \
	--allow-unauthenticated
```


## References

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
