import psycopg2
from config import DATABASE_URL


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is missing. Create a .env file and paste your Neon connection string there."
        )
    return psycopg2.connect(DATABASE_URL)


if __name__ == "__main__":
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                print("Connected successfully!")
                print(cur.fetchone()[0])
    except Exception as exc:
        print(f"Connection failed: {exc}")
