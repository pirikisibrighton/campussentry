
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.storage import get_incidents, save_incident, update_status
from pipeline import analyze

app = FastAPI(title="CampusSentry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)


class IncidentSubmission(BaseModel):
    report_text: str = Field(
        min_length=5,
        max_length=5000,
    )


class StatusUpdate(BaseModel):
    status: str


@app.get("/api/health")
def health():
    return {"message": "CampusSentry API is running"}


@app.get("/api/incidents")
def list_incidents():
    incidents = get_incidents()
    return [
        {
            **incident,
            "reference": f"CS-{incident['id']:05d}",
        }
        for incident in incidents
    ]


@app.post("/api/incidents", status_code=201)
def submit_incident(submission: IncidentSubmission):
    report_text = submission.report_text.strip()

    if len(report_text) < 5:
        raise HTTPException(
            status_code=422,
            detail="Please enter a more detailed incident report.",
        )

    try:
        analysis = analyze(report_text)
        incident_id = save_incident(report_text, analysis)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The incident could not be processed. Please try again.",
        )

    return {
        "message": "Incident report submitted successfully.",
        "reference": f"CS-{incident_id:05d}",
        "incident": {
            "id": incident_id,
            "report_text": report_text,
            **analysis,
            "status": "New",
        },
    }


@app.patch("/api/incidents/{incident_id}/status")
def change_incident_status(
    incident_id: int,
    update: StatusUpdate,
):
    existing = next(
        (
            item for item in get_incidents()
            if item["id"] == incident_id
        ),
        None,
    )

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    try:
        update_status(incident_id, update.status)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    incident = next(
        (
            item for item in get_incidents()
            if item["id"] == incident_id
        ),
        None,
    )

    return {
        **incident,
        "reference": f"CS-{incident_id:05d}",
    }
