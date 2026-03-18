from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.database import save_vitals
from app.agent import run_patient_check
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI(title="John BP Agent API")

# ── Schema ───────────────────────────────────
class VitalReading(BaseModel):
    patient_id: int
    blood_pressure: int
    heart_rate: int
    oxygen_level: float

# ── Routes ───────────────────────────────────
@app.get("/")
def home():
    return {"status": "John BP Agent is running"}

@app.post("/vitals")
def receive_vitals(reading: VitalReading):
    """Receive new vitals from hardware/monitor"""
    save_vitals(
        reading.patient_id,
        reading.blood_pressure,
        reading.heart_rate,
        reading.oxygen_level
    )
    # Run agent check immediately after new reading
    result = run_patient_check(reading.patient_id)
    return {"status": "saved", "agent_result": result}

@app.get("/check/{patient_id}")
def manual_check(patient_id: int):
    """Manually trigger agent check for a patient"""
    result = run_patient_check(patient_id)
    return {"patient_id": patient_id, "result": result}

# ── Auto-check every 30 minutes ──────────────
scheduler = BackgroundScheduler()

@scheduler.scheduled_job("interval", minutes=30)
def scheduled_check():
    print("Running scheduled patient check...")
    run_patient_check(1)  # check John every 30 min

scheduler.start()