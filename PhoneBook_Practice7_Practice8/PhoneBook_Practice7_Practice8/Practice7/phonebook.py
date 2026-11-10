import csv
import re
from pathlib import Path

import psycopg2
from connect import get_connection

PHONE_PATTERN = re.compile(r"^\+?[0-9]{10,15}$")
CSV_PATH = Path(__file__).with_name("contacts.csv")


def valid_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.fullmatch(phone.strip()))


def create_table(conn):
    """Create the contacts table and a case-insensitive unique name index."""
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL UNIQUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    CONSTRAINT contacts_phone_format
                        CHECK (phone ~ '^\\+?[0-9]{10,15}$')
                );
            """)
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS contacts_name_lower_unique
                ON contacts (LOWER(name));
            """)


def show_contacts(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, phone FROM contacts ORDER BY id;")
        rows = cur.fetchall()
    if not rows:
        print("PhoneBook is empty.")
        return
    print("\n--- CONTACTS ---")
    for contact_id, name, phone in rows:
        print(f"{contact_id:>3}. {name} - {phone}")


def add_contact(conn):
    name = input("Full name: ").strip()
    phone = input("Phone (+77011234567): ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    if not valid_phone(phone):
        print("Invalid phone. Use 10-15 digits, optionally starting with +. No spaces or dashes.")
        return
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (name, phone) VALUES (%s, %s) RETURNING id;",
                    (name, phone),
                )
                new_id = cur.fetchone()[0]
        print(f"Contact added. ID: {new_id}")
    except psycopg2.IntegrityError as exc:
        print(f"Could not add contact: this name or phone may already exist. Details: {exc.diag.message_primary}")


def import_csv(conn):
    if not CSV_PATH.exists():
        print(f"CSV file not found: {CSV_PATH}")
        return

    inserted = 0
    skipped = 0
    with open(CSV_PATH, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            print("CSV file is empty or has no header.")
            return

        headers = {header.strip().lower(): header for header in reader.fieldnames}
        name_col = headers.get("name") or headers.get("first_name")
        last_col = headers.get("last_name")
        phone_col = headers.get("phone") or headers.get("phone_number")
        if not name_col or not phone_col:
            print("CSV must have name,phone columns (or first_name,phone_number).")
            return

        for row in reader:
            name = (row.get(name_col) or "").strip()
            if last_col:
                last_name = (row.get(last_col) or "").strip()
                if last_name:
                    name = f"{name} {last_name}".strip()
            phone = (row.get(phone_col) or "").strip()

            if not name or not valid_phone(phone):
                skipped += 1
                print(f"Skipped invalid row: name={name!r}, phone={phone!r}")
                continue

            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO contacts (name, phone)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                            RETURNING id;
                            """,
                            (name, phone),
                        )
                        if cur.fetchone():
                            inserted += 1
                        else:
                            skipped += 1
            except psycopg2.Error as exc:
                skipped += 1
                print(f"Skipped row {name!r}: {exc}")

    print(f"CSV import finished. Inserted: {inserted}; skipped: {skipped}.")


def update_contact(conn):
    current_name = input("Enter the current full name: ").strip()
    if not current_name:
        print("Name cannot be empty.")
        return

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, phone FROM contacts WHERE LOWER(name) = LOWER(%s);",
            (current_name,),
        )
        existing = cur.fetchone()

    if not existing:
        print("Contact not found.")
        return

    contact_id, old_name, old_phone = existing
    print(f"Current contact: {old_name} - {old_phone}")
    new_name = input("New name (press Enter to keep current): ").strip() or old_name
    new_phone = input("New phone (press Enter to keep current): ").strip() or old_phone

    if not valid_phone(new_phone):
        print("Invalid phone number.")
        return

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE contacts SET name = %s, phone = %s WHERE id = %s;",
                    (new_name, new_phone, contact_id),
                )
        print("Contact updated.")
    except psycopg2.IntegrityError as exc:
        print(f"Could not update: this name or phone may already exist. Details: {exc.diag.message_primary}")


def search_contacts(conn):
    term = input("Enter name fragment or phone/prefix: ").strip()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, name, phone
            FROM contacts
            WHERE name ILIKE %s OR phone LIKE %s
            ORDER BY id;
            """,
            (f"%{term}%", f"{term}%"),
        )
        rows = cur.fetchall()
    if rows:
        for contact_id, name, phone in rows:
            print(f"{contact_id}. {name} - {phone}")
    else:
        print("No matching contacts found.")


def delete_contact(conn):
    choice = input("Delete by (1) name or (2) phone? ").strip()
    if choice == "1":
        value = input("Full name: ").strip()
        sql = "DELETE FROM contacts WHERE LOWER(name) = LOWER(%s) RETURNING id, name, phone;"
    elif choice == "2":
        value = input("Phone: ").strip()
        sql = "DELETE FROM contacts WHERE phone = %s RETURNING id, name, phone;"
    else:
        print("Choose 1 or 2.")
        return

    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (value,))
            deleted = cur.fetchall()
    if deleted:
        print("Deleted:", deleted)
    else:
        print("Contact not found.")


def main():
    try:
        conn = get_connection()
        print("Connected to Neon PostgreSQL.")
        create_table(conn)
        print("The contacts table is ready.")

        while True:
            print("\n========== PHONEBOOK ==========")
            print("1. Show all contacts")
            print("2. Add contact")
            print("3. Import contacts from CSV")
            print("4. Update contact")
            print("5. Search contacts")
            print("6. Delete contact")
            print("0. Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                show_contacts(conn)
            elif choice == "2":
                add_contact(conn)
            elif choice == "3":
                import_csv(conn)
            elif choice == "4":
                update_contact(conn)
            elif choice == "5":
                search_contacts(conn)
            elif choice == "6":
                delete_contact(conn)
            elif choice == "0":
                break
            else:
                print("Unknown option. Choose 0-6.")

        conn.close()
        print("Database connection closed.")
    except Exception as exc:
        print(f"Application error: {exc}")


if __name__ == "__main__":
    main()
