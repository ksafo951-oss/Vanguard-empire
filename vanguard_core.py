import os
import json
import time
import requests
import feedparser
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types

# --- 1. SYSTEM STEALTH & LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - OMNI-HARVESTER - %(message)s')

# --- 2. THE CLOUD VAULT (Environment Variables) ---
API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
MY_CHAT_ID = os.environ.get("MY_CHAT_ID")

# [NEW] AUTONOMOUS MAILER CREDENTIALS
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")       # e.g., your_email@gmail.com
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")   # e.g., your Gmail App Password

# --- 3. THE MULTI-HEADED MONETIZATION SUITE ---
STRIPE_STANDARD = "https://buy.stripe.com/your_499_link"
STRIPE_PREMIUM = "https://buy.stripe.com/your_5000_link"
AFFILIATE_LINK = "https://your-affiliate-link.com"

# Initialize the AI Brain
client = genai.Client(api_key=API_KEY)

# --- 4. THE SUPER MEMORY DATABASE ---
MEMORY_FILE = "omni_memory.json"

def load_memory():
    """Loads the database to ensure we never contact the same target twice."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"contacted_targets": []}

def save_memory(company_name):
    """Saves the target to the database permanently."""
    memory = load_memory()
    if company_name not in memory["contacted_targets"]:
        memory["contacted_targets"].append(company_name)
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)

# --- 5. THE DISPATCH ENGINES ---
def notify_omni_harvester(message):
    """Secure encrypted link to your Telegram."""
    if not TELEGRAM_TOKEN or not MY_CHAT_ID:
        logging.warning("Telegram link missing. Printing locally.")
        print(f"\n{message}\n")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": MY_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        logging.error(f"Telegram link severed: {e}")

def execute_autonomous_strike(target_email, subject, body):
    """The Autonomous Mailer. Fires the drafted email to the CEO/Target."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        logging.warning("Email credentials missing in Vault. Bypassing auto-strike.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = target_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Standard Gmail SMTP configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logging.error(f"Auto-strike failed: {e}")
        return False

# --- 6. THE OMNI-REVENUE LOGIC GATE ---
def synthesize_elite_lead(title, link):
    """The Brain: Extracts, Scores, Drafts, and Maps Monetization in one breath."""
    prompt = (
        f"Analyze this market signal: '{title}' (Source: {link}).\n"
        "You are an elite business intelligence AI. Extract the target company, score the lead, "
        "and draft the monetization assets. Return ONLY valid JSON:\n"
        "{\n"
        "  'company_name': 'Name of the company (or SKIP)',\n"
        "  'inferred_email': 'founders@companydomain.com (guess based on name)',\n"
        "  'logic_proof': '1-sentence reason why they have budget right now.',\n"
        "  'monetization_route': 'DIRECT or AFFILIATE',\n"
        "  'free_magnet': 'A high-value industry secret to offer for free.',\n"
        "  'affiliate_pitch': 'A 1-sentence recommendation for the affiliate tool.',\n"
        "  'email_subject': 'A highly clickable, professional cold email subject.',\n"
        "  'email_body': 'A short, 3-sentence cold email offering the free_magnet and a link to my service.',\n"
        "  'viral_blueprint': {'hook': 'Stop-scrolling TikTok hook', 'meat': 'Value delivery', 'cta': 'The closer'},\n"
        "  'precision_score': 10\n"
        "}"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json', temperature=0.1)
        )
        data = json.loads(response.text)
        
        # QUALITY CONTROL: Only the elite 9/10 and 10/10 leads survive.
        if data.get('precision_score', 0) < 9 or data.get('company_name') == 'SKIP':
            return None
        return data

    except Exception as e:
        if "429" in str(e).lower() or "quota" in str(e).lower():
            notify_omni_harvester("⚠️ **QUOTA ALERT:** Hibernating to protect API keys.")
            time.sleep(3600)
        return None

# --- 7. THE GLOBAL SIPHON ENGINE ---
def execute_omni_sweep():
    notify_omni_harvester("🚀 **OMNI-HARVESTER APEX ONLINE.** Scanning vectors & checking memory...")
    memory = load_memory()
    
    vectors = [
        "https://techcrunch.com/feed/", 
        "https://news.ycombinator.com/rss",
        "https://www.venturebeat.com/feed/"
    ]
    
    for vector in vectors:
        try:
            feed = feedparser.parse(requests.get(vector, timeout=10).content)
            for entry in feed.entries[:8]: 
                
                payload = synthesize_elite_lead(entry.title, entry.link)
                
                if payload:
                    company = payload['company_name']
                    
                    # THE SUPER MEMORY CHECK
                    if company in memory['contacted_targets']:
                        logging.info(f"Target {company} already in memory. Bypassing.")
                        continue
                        
                    route = payload['monetization_route']
                    target_email = payload['inferred_email']
                    
                    # EXECUTE AUTONOMOUS EMAIL STRIKE
                    email_body_with_links = payload['email_body'] + f"\n\nSecure the asset here: {STRIPE_PREMIUM if route == 'DIRECT' else AFFILIATE_LINK}"
                    strike_success = execute_autonomous_strike(target_email, payload['email_subject'], email_body_with_links)
                    
                    # UPDATE MEMORY
                    save_memory(company)
                    
                    # DISPATCH THE REPORT TO YOU
                    strike_status = "🟢 EMAIL AUTO-SENT" if strike_success else "🟡 PENDING MANUAL SEND (No Email Keys)"
                    
                    msg = (
                        f"🔱 **OMNI-LEAD SECURED & PROCESSED** 🔱\n\n"
                        f"🎯 **TARGET:** {company}\n"
                        f"📧 **EMAIL:** {target_email}\n"
                        f"⚡ **STATUS:** {strike_status}\n"
                        f"🧠 **LOGIC:** {payload['logic_proof']}\n\n"
                    )
                    
                    if route == "AFFILIATE":
                        msg += f"🔗 **AFFILIATE PITCH:** {payload['affiliate_pitch']}\n\n"
                    else:
                        msg += f"💎 **PREMIUM PIPELINE ACTIVE.**\n\n"
                    
                    msg += (
                        f"🎬 **VIRAL SCRIPT (TikTok/Shorts):**\n"
                        f"🪝 *HOOK:* {payload['viral_blueprint']['hook']}\n"
                        f"💡 *VALUE:* {payload['viral_blueprint']['meat']}\n"
                        f"📣 *CTA:* {payload['viral_blueprint']['cta']}\n"
                    )
                    
                    notify_omni_harvester(msg)
                    time.sleep(15) # Anti-spam and rate-limit protection
                        
        except Exception as e:
            logging.error(f"Vector anomaly: {e}")
            continue

if __name__ == "__main__":
    execute_omni_sweep()
