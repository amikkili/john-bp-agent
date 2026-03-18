import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )

def get_latest_vitals(patient_id: int):
    """Get most recent vitals for a patient"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.*, p.name, p.age, p.medicines
        FROM vitals v
        JOIN patients p ON p.id = v.patient_id
        WHERE v.patient_id = %s
        ORDER BY v.recorded_at DESC
        LIMIT 1
    """, (patient_id,))
    result = cur.fetchone()
    conn.close()
    return dict(result) if result else None

def save_vitals(patient_id, bp, hr, o2):
    """Save new vital reading"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO vitals
          (patient_id, blood_pressure, heart_rate, oxygen_level)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (patient_id, bp, hr, o2))
    conn.commit()
    conn.close()

def save_alert(patient_id, alert_type, message):
    """Log every alert the agent sends"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alerts (patient_id, alert_type, message)
        VALUES (%s, %s, %s)
    """, (patient_id, alert_type, message))
    conn.commit()
    conn.close()