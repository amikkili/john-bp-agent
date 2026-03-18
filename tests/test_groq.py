import sys
import os

# Fix Windows Unicode issue
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("=" * 55)
print("  John BP Agent -- Groq API Connection Test")
print("  (Groq = console.groq.com, key starts with gsk_)")
print("=" * 55)

# ── Check .env loaded ────────────────────────────────────────
groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    print("\n[FAIL]  GROQ_API_KEY not found in .env file")
    print("        Fix -> Open your .env file and add:")
    print("        GROQ_API_KEY=gsk_your_key_here")
    print()
    print("        Get key from: console.groq.com")
    print("        -> Login -> API Keys -> Create API Key")
    exit(1)

if not groq_key.startswith("gsk_"):
    print("\n[FAIL]  Key looks wrong")
    print(f"        Your key starts with: {groq_key[:8]}...")
    print("        Groq keys must start with 'gsk_'")
    print("        Fix -> Go to console.groq.com and copy your key")
    exit(1)

print(f"\n[OK]  GROQ_API_KEY found in .env")
print(f"      Key starts with: {groq_key[:12]}...")

# ── Test 1: Create Groq client ───────────────────────────────
print("\n-- Test 1: Connect to Groq API ------------------------")
try:
    groq = OpenAI(
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1"
    )
    print("[OK]  Groq client created successfully")

except Exception as e:
    print(f"[FAIL]  Failed to create Groq client: {e}")
    exit(1)

# ── Test 2: Simple ping ──────────────────────────────────────
print("\n-- Test 2: Basic Groq response ------------------------")
try:
    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": "Reply with exactly 5 words: Groq API is working correctly"
        }],
        max_tokens=20
    )
    reply = response.choices[0].message.content
    print(f"[OK]  Groq responded!")
    print(f"      Response: {reply}")

except Exception as e:
    print(f"[FAIL]  Groq API call failed: {e}")
    print("\n        Common fixes:")
    print("        1. Check API key at console.groq.com")
    print("        2. Make sure key starts with gsk_")
    print("        3. Check your internet connection")
    exit(1)

# ── Test 3: Medical reasoning — the real test ────────────────
print("\n-- Test 3: Medical reasoning (the real test) ----------")
print("      Asking Groq about John's condition...")
print("      Please wait a few seconds...\n")

try:
    medical_prompt = """
You are a clinical AI assistant. Analyse this patient data
and give a structured response.

Patient: John
Age: 67 years old
Blood Pressure: 155/95 mmHg  (normal is below 120/80)
Heart Rate: 98 bpm           (normal is 60-100)
Oxygen Level: 94%            (normal is 95-100%)
Current Medicines: Warfarin, Aspirin, Lisinopril

Answer in exactly this format:

RISK LEVEL: [LOW / MEDIUM / HIGH / CRITICAL]
REASON: [one sentence explaining the main risk]
DRUG WARNING: [YES or NO]
DRUG DETAIL: [if YES, explain which drugs conflict and why]
DOCTOR ACTION: [what should the doctor do right now?]
"""

    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",            # Groq model
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical AI assistant. "
                    "Be precise and always prioritise patient safety."
                )
            },
            {
                "role": "user",
                "content": medical_prompt
            }
        ],
        max_tokens=300
    )

    answer = response.choices[0].message.content

    print("[OK]  Groq analysed John's condition!\n")
    print("-" * 55)
    print(answer)
    print("-" * 55)

    # Check Groq correctly identified the drug conflict
    answer_lower = answer.lower()
    if "warfarin" in answer_lower and "aspirin" in answer_lower:
        print("\n[OK]  Groq correctly identified Warfarin + Aspirin conflict!")
        print("      Your AI brain is working perfectly!")
        print("      You are ready to build the full agent!")
    else:
        print("\n[WARN]  Groq responded but may not have flagged drug conflict")
        print("        Try running the test again")

except Exception as e:
    print(f"[FAIL]  Medical reasoning test failed: {e}")
    exit(1)

# ── Test 4: Token usage ──────────────────────────────────────
print("\n-- Test 4: Token usage --------------------------------")
try:
    usage = response.usage
    print(f"[OK]  Token usage:")
    print(f"      Input tokens  : {usage.prompt_tokens}")
    print(f"      Output tokens : {usage.completion_tokens}")
    print(f"      Total tokens  : {usage.total_tokens}")
    print(f"      Cost          : FREE on Groq!")
    print(f"      Rate limit    : 6000 tokens/min on free tier")

except Exception as e:
    print(f"      Could not fetch usage info: {e}")

# ── Final summary ────────────────────────────────────────────
print("\n" + "=" * 55)
print("  Groq API test complete!")
print()
print("  NEXT STEPS:")
print("  1. Both test_db.py and test_grok.py passed [OK]?")
print("  2. Update your .env file:")
print("     - rename GROK_API_KEY to GROQ_API_KEY")
print("  3. Go back to the step-by-step guide")
print("  4. Start building tools.py  (Step 4 in guide)")
print("=" * 55)
