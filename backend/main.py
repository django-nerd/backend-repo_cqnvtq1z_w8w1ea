from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Neurodek API", version="1.0.0")

# CORS for local dev + hosted preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    budget: Optional[str] = None
    message: str

@app.get("/")
async def root():
    return {"message": "Neurodek API is running"}

@app.get("/test")
async def test():
    # In a real app we'd check DB; here we return environment info for diagnostics
    return {
        "backend": "fastapi",
        "database": "mongodb",
        "database_url": os.getenv('DATABASE_URL', 'not-set'),
        "database_name": os.getenv('DATABASE_NAME', 'not-set'),
        "connection_status": "ok"
    }

@app.post("/contact")
async def submit_contact(payload: ContactRequest):
    # Normally we'd persist to DB or send email; we'll accept and echo minimal fields
    if not payload.name or not payload.message:
        raise HTTPException(status_code=400, detail="Missing fields")
    return {"status": "received", "name": payload.name}
