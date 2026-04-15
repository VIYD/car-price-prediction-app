# Streamlit Frontend

This frontend is a Streamlit app that uses the backend API:

- `GET /metadata` for form options
- `POST /predict` for price estimation

## Local run

1. Start backend on port `8000`.
2. In this folder, install dependencies from `requirements.txt`.
3. Run Streamlit app from this folder.

The app uses `BACKEND_URL` environment variable and defaults to `http://localhost:8000`.

## Docker Compose

From project root, run Docker Compose. Frontend is available at:

- `http://localhost:8501`

## Troubleshooting

- If metadata fails to load, check backend container logs and ensure backend is healthy.
- If prediction fails, verify payload fields and that model artifacts are present in backend.