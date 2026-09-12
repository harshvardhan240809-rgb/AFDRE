# MAYDAY AI

MAYDAY AI is a local demo application for a resilient system incident response scenario. It combines a FastAPI backend, a React + Vite frontend, and a deterministic simulation engine to model failure injection, recovery planning, chaos events, and verification.

## Features
- Digital twin service graph with health, latency, and load indicators
- Failure scenario selection and chaos injection
- Recovery plan generation and verification flow
- Incident memory and recent risk audit panels
- Local demo mode with deterministic, no-external-API behavior

## Run locally

### Backend
1. Open a terminal in the workspace root.
2. Start the backend:

   C:\Users\harsh\OneDrive\Desktop\AFDRE\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

3. Health check:

   http://127.0.0.1:8000/health

### Frontend
1. In a second terminal, change into the frontend folder.
2. Start the dev server:

   cd frontend
   npm install
   npm run dev -- --host 127.0.0.1

3. Open:

   http://127.0.0.1:5173

## Verification
- Backend tests:

  $env:PYTHONPATH = 'backend'
  C:\Users\harsh\OneDrive\Desktop\AFDRE\.venv\Scripts\python.exe -m pytest backend\tests\test_engine.py

- Frontend build:

  cd frontend
  npm run build

## Notes
- The app runs entirely locally for demo purposes.
- The backend uses in-memory state and seeded incident memory.
- The default scenario is `Payment Gateway Failure`.
