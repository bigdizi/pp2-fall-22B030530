import os
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent

# Prefer a TSIS1/.env file, but also reuse Practice7/.env from the old project.
load_dotenv(HERE / ".env")
load_dotenv(HERE.parent / "Practice7" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
