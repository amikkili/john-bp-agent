import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS patients (
  id         SERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  age        INTEGER,
  medicines  TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vitals (
  id             SERIAL PRIMARY KEY,
  patient_id     INTEGER REFERENCES patients(id),
  blood_pressure INTEGER,
  heart_rate     INTEGER,
  oxygen_level   FLOAT,
  recorded_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerts (
  id         SERIAL PRIMARY KEY,
  patient_id INTEGER REFERENCES patients(id),
  alert_type TEXT,
  message    TEXT,
  sent_at    TIMESTAMPTZ DEFAULT NOW()
);
""")

# Insert John only if not already there
cur.execute("""
INSERT INTO patients (name, age, medicines)
SELECT 'John', 67, ARRAY['Warfarin','Aspirin','Lisinopril']
WHERE NOT EXISTS (
  SELECT 1 FROM patients WHERE name = 'John'
);
""")

# Insert first vital reading for John
cur.execute("""
INSERT INTO vitals (patient_id, blood_pressure, heart_rate, oxygen_level)
VALUES (1, 155, 98, 94.5);
""")

conn.commit()
print("Tables created successfully")

# Verify
cur.execute("SELECT * FROM patients")
print("Patients:", cur.fetchall())

cur.execute("SELECT * FROM vitals")
print("Vitals:", cur.fetchall())

conn.close()