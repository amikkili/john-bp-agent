from database import get_latest_vitals, save_alert
from groq_client import ask_groq
from alerts import send_whatsapp

# ── Tool 1 ──────────────────────────────────
@tool
def check_patient_vitals(patient_id: int) -> str:
    """
    Fetch the latest vitals for a patient from DB.
    Returns blood pressure, heart rate, oxygen level
    and list of their current medicines.
    Use this first before any analysis.
    """
    data = get_latest_vitals(patient_id)
    if not data:
        return "No vitals found for this patient"
    return (
        f"Patient: {data['name']}, Age: {data['age']}\n"
        f"BP: {data['blood_pressure']}, "
        f"HR: {data['heart_rate']}, "
        f"O2: {data['oxygen_level']}%\n"
        f"Medicines: {', '.join(data['medicines'])}"
    )

# ── Tool 2 ──────────────────────────────────
@tool
def analyse_risk(patient_data: str) -> str:
    """
    Send patient vitals and medicines to Grok AI.
    Returns risk assessment and recommended action.
    Use this after fetching vitals to analyse risk.
    """
    prompt = f"""
    Analyse this patient and respond in exactly this format:
    RISK_LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
    DRUG_CONFLICT: [YES/NO] - reason if yes
    ACTION: [what doctor must do]
    URGENCY: [IMMEDIATE/WITHIN_1HR/MONITOR]

    Patient data:
    {patient_data}
    """
    return ask_grok(prompt)

# ── Tool 3 ──────────────────────────────────
@tool
def alert_doctor(patient_id: int, message: str) -> str:
    """
    Send an urgent WhatsApp alert to the doctor.
    Use this when risk level is HIGH or CRITICAL,
    or when a dangerous drug conflict is found.
    """
    send_whatsapp(message)
    save_alert(patient_id, "WHATSAPP", message)
    return f"Alert sent to doctor: {message[:50]}..."

# Export all tools as a list
TOOLS = [check_patient_vitals, analyse_risk, alert_doctor]