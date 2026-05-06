# Walmart Product AI Summarizer

An AI-powered application that analyzes Walmart product reviews, cleans and stores the review data, and generates a concise summary with pros, cons, and a recommendation.

## What This Project Does

Given a Walmart product URL, the application:

1. Extracts the Walmart product ID
2. Scrapes customer reviews using SerpAPI
3. Cleans and standardizes the review data
4. Stores the cleaned reviews in Amazon S3
5. Sends the reviews to AWS Bedrock for summarization
6. Displays the final AI-generated review summary in a Streamlit UI

## Architecture

This project uses a layered service architecture.

- Frontend layer: Streamlit user interface
- API layer: FastAPI routes
- Service layer: business logic and workflow orchestration
- Client/adapter layer: integrations with SerpAPI, S3, and Bedrock
- Domain layer: review cleaning logic
- Schema layer: request and response contracts

This structure keeps HTTP handling, business workflow, and external integrations separated, which makes the codebase easier to maintain and extend.

## Project Structure

```text
frontend/
  streamlit_app.py
  utils/api.py

backend/
  api/routes/
  app/main.py
  clients/
  config/
  domain/
  schemas/
  services/
  shared/
```

### Backend Layers

- `backend/app/main.py`
  - FastAPI app setup and router registration
- `backend/api/routes/`
  - thin HTTP route handlers
- `backend/services/`
  - workflow logic for product ID extraction, scraping, cleaning, and summarization
- `backend/clients/`
  - wrappers for SerpAPI, S3, and Bedrock
- `backend/domain/`
  - review cleaning rules
- `backend/schemas/`
  - Pydantic request and response models
- `backend/config/`
  - centralized settings

## End-to-End Flow

```text
User -> Streamlit Frontend -> FastAPI Backend -> Services -> External Systems
                                                   |-> SerpAPI
                                                   |-> Amazon S3
                                                   |-> AWS Bedrock
```

## Diagrams

### System Design

Add the system design diagram link here.

`<img width="1621" height="668" alt="walmart_system_design" src="https://github.com/user-attachments/assets/8ae9e424-c424-4860-bf06-1738fc3b4e68" />`

### Pipeline Design

Add the pipeline design diagram link here.

`<img width="1400" height="900" alt="walmart_diagram1" src="https://github.com/user-attachments/assets/4431a107-1933-4afb-950b-0de246eb9bc7" />`

Detailed request flow:

1. User enters a Walmart product URL in the Streamlit app
2. Frontend calls `/extract_id`
3. Frontend calls `/scrape`
4. Backend checks whether cleaned review data already exists in S3
5. If not cached, reviews are scraped and sent to `/data_clean`
6. Cleaned reviews are uploaded to S3
7. Frontend calls `/summarize`
8. Backend loads the cleaned CSV from S3 and sends the review text to Bedrock
9. Summary is returned to the UI

## API Endpoints

- `GET /health`
  - health check
- `POST /extract_id`
  - extracts Walmart product ID from a product URL
- `POST /scrape`
  - scrapes Walmart review data or returns cached S3 metadata
- `POST /data_clean`
  - cleans raw reviews and uploads the CSV to S3
- `POST /summarize`
  - loads reviews from S3 and returns an AI-generated summary

## Environment Variables

Set these before running the project:

```text
API_BASE=http://localhost:8000
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
SERPAPI_KEY=your-serpapi-key
S3_BUCKET=walmart-scraped-data
BEDROCK_MODEL_ID=qwen.qwen3-32b-v1:0
```

## Running Locally

The frontend and backend run as separate applications.

### Backend

Run from the project root:

```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

Run in a second terminal from the project root:

```bash
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

Then open:

- Frontend: `http://localhost:8501`
- Backend docs: `http://localhost:8000/docs`

## Running with Docker Compose

From the project root:

```bash
docker compose up --build
```

This starts:

- FastAPI backend on port `8000`
- Streamlit frontend on port `8501`

## Testing

Run backend tests from the project root:

```bash
pip install -r backend/requirements.txt
python -m pytest tests
```

GitHub Actions also runs the test suite automatically on pushes and pull requests.

## Key Design Decisions

- Frontend and backend are separated
  - UI concerns stay independent from backend logic
- Routes are thin
  - API handlers only validate input and call services
- Services contain workflow logic
  - easier to test and extend
- External systems are isolated in clients
  - easier to swap providers later
- S3 is used as a cache and storage layer
  - avoids repeated scraping and cleaning for the same product

## Tech Stack

- Python
- Streamlit
- FastAPI
- Pandas
- SerpAPI
- Amazon S3
- AWS Bedrock
- Docker

## Current Notes

- The frontend depends on the backend being reachable through `API_BASE`
- The summarization flow assumes cleaned review CSVs are stored in S3
- AWS credentials and SerpAPI credentials must be configured for the app to work end to end
