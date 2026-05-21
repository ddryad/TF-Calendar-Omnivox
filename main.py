from fastapi import FastAPI, HTTPException
from models import CredentialsRequest, ClassItem
from scraper import login, get_classes, parse_classe
from typing import List

app = FastAPI(
    title="TF-Calendar Omnivox Service",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classes", response_model=List[ClassItem])
def fetch_classes(credentials: CredentialsRequest):
    try:
        session = login(credentials.da, credentials.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Omnivox unreachable: {str(e)}")

    try:
        classes = get_classes(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    return [parse_classe(c) for c in classes] 
