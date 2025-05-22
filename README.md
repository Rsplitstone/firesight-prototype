# FireSight Prototype

This repository contains a basic frontend prototype (`index.html`) and a FastAPI backend used for experimentation.

## Running the API

1. Install dependencies (preferably in a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
2. Start the development server:
   ```bash
   uvicorn api.main:app --reload
   ```

The API provides automatic Swagger documentation at `http://localhost:8000/docs`.
