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

# --- Scheduler Configuration ---
TIMEZONE = pytz.timezone("US/Eastern")
