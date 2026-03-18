# ============================================================
#  test_db.py  —  Test your Render PostgreSQL connection
#  Run:  python test_db.py
#  Windows-compatible version (no emoji)
# ============================================================

import sys
import os

# Fix Windows Unicode issue — must be at the very top
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

print("=" * 55)
print("  John BP Agent -- PostgreSQL Connection Test")
print("=" * 55)

# ── Check .env loaded ────────────────────────────────────────
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("\n[FAIL]  DATABASE_URL not found in .env file")
    print("        Fix -> Open .env and add:")
    print("        DATABASE_URL=postgresql://user:pass@host/dbname")
    exit(1)

print(f"\n[OK]  DATABASE_URL found in .env")
print(f"      Connecting to: {db_url[:45]}...")

# ── Test 1: Basic connection ─────────────────────────────────
print("\n-- Test 1: Connect to PostgreSQL ----------------------")
try:
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"[OK]  Connected!")
    print(f"      {str(version['version'])[:70]}")

except psycopg2.OperationalError as e:
    print(f"[FAIL]  Connection failed: {e}")
    print("\n        Common fixes:")
    print("        1. Use External URL from Render (not Internal)")
    print("        2. Add ?sslmode=require at end of DATABASE_URL")
    print("           postgresql://user:pass@host/db?sslmode=require")
    exit(1)

# ── Test 2: Check tables exist ───────────────────────────────
print("\n-- Test 2: Check tables exist -------------------------")
try:
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('patients', 'vitals', 'alerts')
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    table_names = [t['table_name'] for t in tables]

    all_found = True
    for name in ['alerts', 'patients', 'vitals']:
        if name in table_names:
            print(f"[OK]    Table '{name}' exists")
        else:
            print(f"[FAIL]  Table '{name}' NOT found")
            print(f"        Fix -> Run the CREATE TABLE SQL from setup guide")
            all_found = False

    if not all_found:
        print("\n        Run the SQL in Part 1 Step 4 of the setup guide")
        conn.close()
        exit(1)

except Exception as e:
    print(f"[FAIL]  Error checking tables: {e}")
    conn.close()
    exit(1)

# ── Test 3: Find John ────────────────────────────────────────
print("\n-- Test 3: Find patient John --------------------------")
try:
    cur.execute("SELECT * FROM patients WHERE name = 'John';")
    john = cur.fetchone()

    if john:
        print(f"[OK]  John found in database!")
        print(f"      ID        : {john['id']}")
        print(f"      Name      : {john['name']}")
        print(f"      Age       : {john['age']}")
        print(f"      Medicines : {john['medicines']}")
    else:
        print("[FAIL]  John NOT found in patients table")
        print("        Fix -> Run this SQL in your database:")
        print("        INSERT INTO patients (name, age, medicines)")
        print("        VALUES ('John', 67, ARRAY['Warfarin','Aspirin','Lisinopril']);")

except Exception as e:
    print(f"[FAIL]  Error fetching John: {e}")
    conn.close()
    exit(1)

# ── Test 4: Fetch vitals ─────────────────────────────────────
print("\n-- Test 4: Fetch John's vitals ------------------------")
try:
    cur.execute("""
        SELECT v.blood_pressure, v.heart_rate,
               v.oxygen_level, v.recorded_at
        FROM vitals v
        JOIN patients p ON p.id = v.patient_id
        WHERE p.name = 'John'
        ORDER BY v.recorded_at DESC
        LIMIT 1;
    """)
    vitals = cur.fetchone()

    if vitals:
        print(f"[OK]  Vitals found!")
        print(f"      Blood Pressure : {vitals['blood_pressure']} mmHg")
        print(f"      Heart Rate     : {vitals['heart_rate']} bpm")
        print(f"      Oxygen Level   : {vitals['oxygen_level']}%")
        print(f"      Recorded at    : {vitals['recorded_at']}")
    else:
        print("[FAIL]  No vitals found for John")
        print("        Fix -> Run this SQL:")
        print("        INSERT INTO vitals")
        print("          (patient_id, blood_pressure, heart_rate, oxygen_level)")
        print("        VALUES (1, 155, 98, 94.5);")

except Exception as e:
    print(f"[FAIL]  Error fetching vitals: {e}")

finally:
    conn.close()

# ── Summary ──────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  Database test complete!")
print("  If all 4 tests show [OK] -- run test_grok.py next")
print("=" * 55)
