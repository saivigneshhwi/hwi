#!/bin/bash
# Start FastAPI app with Gunicorn and Uvicorn worker
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001 --workers 4
