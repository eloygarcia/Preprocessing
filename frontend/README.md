# Frontend example

This folder contains a minimal React + Vite example that can call the FastAPI backend and later host a Cornerstone DICOM viewer.

## Run it

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start the dev server:
   ```bash
   npm run dev
   ```
3. Start the backend:
   ```bash
   cd ..
   uvicorn api.main:app --reload --port 8000
   ```