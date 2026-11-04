from pathlib import Path
from dotenv import load_dotenv

# Load the project-level .env before modules import the database or secrets.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / '.env')
load_dotenv(Path(__file__).resolve().parents[1] / '.env', override=False)
