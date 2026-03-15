import os
import time
import json
import logging
import requests
import feedparser
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load Secrets from Environment
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

MEMORY_FILE = "omni_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {"contacted_targets": [], "last_run": None}

def save_memory(company_name):
    memory = load_memory()
    if company_name not in memory['contacted_targets']:
        memory['contacted_targets'].append(company_name)
    memory['last_run'] = datetime.now().isoformat()
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)

def notify_omni_harvester(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Telegram failed: {e}")

def synthesize_elite_lead(title, link):
    prompt = f"""
    Analyze this business signal: {title} ({link})
    1. Identify Company Name.
    2. Determine if they need AI Automation, Workflow Optimization, or Lead Gen.
    3. Infer a likely professional email format.
    4. Create a Viral TikTok Hook.
    5. Output ONLY as valid JSON:
    {{
        "company_name": "Name",
        "monetization_route": "PREMIUM/AFFILIATE",
        "inferred_email": "contact@company.com",
        "email_subject": "Quick Question",
        "logic_proof": "Why this is a lead",
        "viral_blueprint": {{"hook": "...", "meat": "...", "cta": "..."}},
        "affiliate_pitch": "optional"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Clean potential markdown from response
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        if "429" in str(e):
            logging.warning("Quota reached. Entering short hibernation.")
            return "QUOTA_HIT"
        logging.error(f"AI Synthesis Error: {e}")
        return None

def execute_omni_sweep():
    logging.info("🚀 OMNI-HARVESTER APEX IGNITION")
    memory = load_memory()
    
    # Add your RSS feeds or "Vectors" here
    vectors = [
        "https://hnrss.org/newest?q=startup",
        "https://www.google.com/alerts/feeds/12345/67890" # Replace with your actual feeds
    ]

    for vector in vectors:
        try:
            logging.info(f"Scanning Vector: {vector}")
            feed = feedparser.parse(requests.get(vector, timeout=10).content)
            
            for entry in feed.entries[:8]:
                payload = synthesize_elite_lead(entry.title, entry.link)

                if payload == "QUOTA_HIT":
                    notify_omni_harvester("⚠️ **QUOTA ALERT:** Hibernating for this cycle to protect API keys.")
                    return

                if payload:
                    company = payload['company_name']
                    if company in memory['contacted_targets']:
                        continue

                    # Prep Message
                    msg = (
                        f"🔱 **OMNI-LEAD SECURED** 🔱\n\n"
                        f"🎯 **TARGET:** {company}\n"
                        f"📧 **EMAIL:** {payload['inferred_email']}\n"
                        f"🧠 **LOGIC:** {payload['logic_proof']}\n\n"
                        f"🎬 **VIRAL HOOK:** {payload['viral_blueprint']['hook']}"
                    )
                    
                    notify_omni_harvester(msg)
                    save_memory(company)
                    logging.info(f"✅ Success: {company}")

                # THE BREATHER: 10 seconds between every entry to stay under free tier limits
                time.sleep(10)

        except Exception as e:
            logging.error(f"Vector anomaly: {e}")
            continue

    logging.info("🏁 Sweep Completed Successfully.")

if __name__ == "__main__":
    execute_omni_sweep()
