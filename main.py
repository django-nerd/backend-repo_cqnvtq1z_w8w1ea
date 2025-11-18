import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Database helpers (pymongo under the hood)
from database import create_document, db

app = FastAPI(title="Neurodek API")

# CORS: open for development/preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    company: Optional[str] = None
    budget: Optional[str] = None
    message: str = Field(..., min_length=5, max_length=5000)


@app.get("/")
def root():
    return {"message": "Neurodek API is running"}


@app.get("/test")
def test_database():
    """Diagnostic endpoint to verify backend and database connectivity"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        # Env check
        database_url = os.getenv("DATABASE_URL")
        database_name = os.getenv("DATABASE_NAME")
        response["database_url"] = "✅ Set" if database_url else "❌ Not Set"
        response["database_name"] = "✅ Set" if database_name else "❌ Not Set"

        if db is not None:
            response["database"] = "✅ Available"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:120]}"
        else:
            response["database"] = "⚠️ Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"

    return response


@app.post("/contact")
def contact(payload: ContactRequest):
    """Accepts contact submissions and stores them in MongoDB."""
    try:
        # Persist to DB if available
        doc_id = None
        if db is None:
            # In environments without DB, skip persistence but still respond success
            doc_id = None
        else:
            doc_id = create_document("contact", payload)

        return {
            "status": "ok",
            "name": payload.name,
            "id": doc_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit: {str(e)[:200]}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
