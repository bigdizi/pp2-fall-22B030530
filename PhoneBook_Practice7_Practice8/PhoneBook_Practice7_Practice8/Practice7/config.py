import os
from dotenv import load_dotenv

# Read DATABASE_URL from the local .env file.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
