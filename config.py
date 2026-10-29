import os
import pytz
from dotenv import load_dotenv

# Load environment variables from the .env file in the same directory
load_dotenv()

# --- INKR Credentials ---
INKR_EMAIL = os.getenv("INKR_EMAIL")
INKR_PASSWORD = os.getenv("INKR_PASSWORD")

# --- Google Workspace ---
# One sheet per team; TODO: confirm real IDs and what each team's sheet tracks.
GOOGLE_SHEET_IDS = {
    "team_1": os.getenv("GOOGLE_SHEET_ID_TEAM_1"),
    "team_2": os.getenv("GOOGLE_SHEET_ID_TEAM_2"),
    "team_3": os.getenv("GOOGLE_SHEET_ID_TEAM_3"),
}
GSPREAD_SERVICE_ACCOUNT_FILE = os.getenv("GSPREAD_SERVICE_ACCOUNT_FILE", "service_account.json")

# --- PM Layer Configuration ---
# Used only by pm_layer.RealLLMClient and notifier.SMTPEmailClient — not
# needed for the mock pipeline. See claude_update.md for the cost reasoning.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
PM_REPORT_RECIPIENT = os.getenv("PM_REPORT_RECIPIENT", "minh@octopistudio.com")

# --- Scheduler Configuration ---
TIMEZONE = pytz.timezone("US/Eastern")
