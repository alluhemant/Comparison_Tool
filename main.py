from fastapi import FastAPI
from app.api.endpoints import router  # Import the unified router
from app.data.db import DBHandler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    DBHandler()

app.include_router(router)  # This now includes /api/v1/compare, /api/v1/history, etc.

@app.get("/")
def read_root():
    return {"message": "API Comparison Service"}