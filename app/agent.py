import json
import os
from groq import Groq
from dotenv import load_dotenv
from app.database import get_latest_vitals, save_alert
from app.groq_client import ask_groq
from app.alerts import send_whatsapp

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Define tools the agent can call ─────────
TOOLS = [
  {
    "type": "function",
    "function": {
      "name": "check_patient_vitals",
      "description": "Fetch latest vitals for a patient from DB",
      "parameters": {
        "type": "object",
        "properties": {
          "patient_id": {"type": "integer"}
        },
        "required": ["patient_id"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "analyse_risk",
      "description": "Analyse patient vitals and medicines for risk",
      "parameters": {
        "type": "object",
        "properties": {
          "patient_data": {"type": "string"}
        },
        "required": ["patient_data"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "alert_doctor",
      "description": "Send WhatsApp alert to doctor",
      "parameters": {
        "type": "object",
        "properties": {
          "patient_id": {"type": "integer"},
          "message":    {"type": "string"}
        },
        "required": ["patient_id", "message"]
      }
    }
  }
]

# ── Execute whichever tool Groq chose ────────
def execute_tool(name: str, args: dict) -> str:
    print(f" Calling tool: {name}({args})")

    if name == "check_patient_vitals":
        data = get_latest_vitals(args["patient_id"])
        if not data:
            return "No vitals found"
        return (
            f"Patient: {data['name']}, Age: {data['age']}\n"
            f"BP: {data['blood_pressure']}, "
            f"HR: {data['heart_rate']}, "
            f"O2: {data['oxygen_level']}%\n"
            f"Medicines: {', '.join(data['medicines'])}"
        )

    elif name == "analyse_risk":
        prompt = f"""Analyse this patient:
{args['patient_data']}

Reply in this exact format:
RISK_LEVEL: HIGH or CRITICAL or MEDIUM or LOW
DRUG_CONFLICT: YES or NO - reason
ACTION: what doctor must do
URGENCY: IMMEDIATE or MONITOR"""
        return ask_groq(prompt)

    elif name == "alert_doctor":
        pid = args["patient_id"]
        msg = args["message"]
        send_whatsapp(msg)
        save_alert(pid, "WHATSAPP", msg)
        return f"Alert sent: {msg[:60]}"

    return "Unknown tool"

# ── Main agent loop ──────────────────────────
def run_patient_check(patient_id: int) -> str:
    print(f" Agent starting for patient {patient_id}")

    messages = [{
        "role": "system",
        "content": """You are a clinical AI monitoring agent.
For every patient check you MUST:
1. Call check_patient_vitals first
2. Call analyse_risk with the vitals data
3. If risk is HIGH or CRITICAL → call alert_doctor
4. Return a final summary"""
    }, {
        "role": "user",
        "content": f"Check patient {patient_id} now."
    }]

    # Agent loop — runs until Groq stops calling tools
    for _ in range(10):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        # No more tool calls → agent is done
        if not msg.tool_calls:
            print(f" Agent done \n{msg.content}")
            return msg.content

        # Execute each tool Groq requested
        messages.append(msg)
        for tc in msg.tool_calls:
            result = execute_tool(
                tc.function.name,
                json.loads(tc.function.arguments)
            )
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return "Agent completed max iterations"