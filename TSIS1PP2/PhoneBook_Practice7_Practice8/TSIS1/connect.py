import psycopg2

from config import DATABASE_URL


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is missing. Add it to TSIS1/.env or Practice7/.env."
        )
    return psycopg2.connect(DATABASE_URL)
