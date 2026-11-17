"""TSIS 1 - Extended PhoneBook application.

Practice 7 CRUD and Practice 8 database objects are reused. This module adds
extended contact fields, multiple phones, filtering, sorting, JSON exchange,
and calls the new TSIS 1 procedures/function.
"""

import csv
import json
import re
from datetime import date
from pathlib import Path
from typing import Optional

import psycopg2
from connect import get_connection

PHONE_PATTERN = re.compile(r"^\+?[0-9]{10,15}$")
PHONE_TYPES = {"home", "work", "mobile"}
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "contacts.csv"
JSON_PATH = BASE_DIR / "contacts.json"
PAGE_SIZE = 5


def valid_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.fullmatch((phone or "").strip()))


def normalize_birthday(value: Optional[str]):
    """Return a date object for YYYY-MM-DD input, or None for an empty value."""
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Birthday must use YYYY-MM-DD format.") from exc


def get_group_id(cur, group_name: Optional[str]):
    """Find a group case-insensitively; create it if a non-empty name is given."""
    group_name = (group_name or "").strip()
    if not group_name:
        return None

    cur.execute(
        'SELECT id FROM "groups" WHERE LOWER(name) = LOWER(%s) LIMIT 1;',
        (group_name,),
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO "groups" (name)
        VALUES (%s)
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
        """,
        (group_name,),
    )
    return cur.fetchone()[0]


def check_schema(conn):
    """Fail early with a useful message if the TSIS 1 migration was not run."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                to_regclass('public.contacts'),
                to_regclass('public."groups"'),
                to_regclass('public.phones'),
                to_regprocedure('public.get_contacts_paginated(integer,integer)'),
                EXISTS (
                    SELECT 1 FROM pg_proc p
                    JOIN pg_namespace n ON n.oid = p.pronamespace
                    WHERE n.nspname = 'public' AND p.proname = 'add_phone' AND p.prokind = 'p'
                ),
                EXISTS (
                    SELECT 1 FROM pg_proc p
                    JOIN pg_namespace n ON n.oid = p.pronamespace
                    WHERE n.nspname = 'public' AND p.proname = 'move_to_group' AND p.prokind = 'p'
                ),
                to_regprocedure('public.search_contacts(text)');
            """
        )
        objects = cur.fetchone()

    labels = [
        "contacts table (Practice 7)",
        "groups table (TSIS 1)",
        "phones table (TSIS 1)",
        "get_contacts_paginated function (Practice 8)",
        "add_phone procedure (TSIS 1)",
        "move_to_group procedure (TSIS 1)",
        "search_contacts function (TSIS 1)",
    ]
    missing = [
        label for label, obj in zip(labels, objects)
        if (obj is None or obj is False)
    ]
    if missing:
        raise RuntimeError(
            "Database setup is incomplete. Run Practice 7 first, then TSIS1/schema.sql "
            "and TSIS1/procedures.sql in Neon. Missing: " + ", ".join(missing)
        )


def fetch_contact_rows(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                c.id,
                c.name,
                c.email,
                c.birthday,
                g.name AS group_name,
                c.created_at,
                COALESCE(
                    (
                        SELECT STRING_AGG(p.phone || ' [' || p.type || ']', ', ' ORDER BY p.id)
                        FROM phones AS p
                        WHERE p.contact_id = c.id
                    ),
                    c.phone
                ) AS phone_list
            FROM contacts AS c
            LEFT JOIN "groups" AS g ON g.id = c.group_id
            ORDER BY c.id;
            """
        )
        return cur.fetchall()


def print_contact_rows(rows):
    if not rows:
        print("No contacts found.")
        return

    print("\n--- PHONEBOOK ---")
    for contact_id, name, email, birthday, group_name, created_at, phone_list in rows:
        print(f"\nID: {contact_id} | Name: {name}")
        print(f"Phones: {phone_list or '—'}")
        print(f"Email: {email or '—'}")
        print(f"Birthday: {birthday or '—'}")
        print(f"Group: {group_name or 'Other / not assigned'}")
        print(f"Date added: {created_at}")


def show_contacts(conn):
    print_contact_rows(fetch_contact_rows(conn))


def add_contact(conn):
    """Extended version of the existing Practice 7 console add operation."""
    name = input("Full name: ").strip()
    phone = input("Main phone (+77011234567): ").strip()
    email = input("Email (optional): ").strip() or None
    birthday_text = input("Birthday YYYY-MM-DD (optional): ").strip()
    group_name = input("Group Family/Work/Friend/Other (optional): ").strip()
    phone_type = input("Phone type home/work/mobile [mobile]: ").strip().lower() or "mobile"

    if not name:
        print("Name cannot be empty.")
        return
    if not valid_phone(phone):
        print("Invalid phone. Use 10-15 digits, optionally starting with +.")
        return
    if phone_type not in PHONE_TYPES:
        print("Phone type must be home, work, or mobile.")
        return

    try:
        birthday = normalize_birthday(birthday_text)
        with conn:
            with conn.cursor() as cur:
                group_id = get_group_id(cur, group_name)
                cur.execute(
                    """
                    INSERT INTO contacts (name, phone, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (name, phone, email, birthday, group_id),
                )
                contact_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                    (contact_id, phone, phone_type),
                )
        print(f"Contact added. ID: {contact_id}")
    except (ValueError, psycopg2.Error) as exc:
        print(f"Could not add contact: {exc}")


def import_csv(conn):
    """Extend the original Practice 7 CSV importer with optional TSIS 1 fields.

    Accepted headers: name/first_name, last_name, phone/phone_number, email,
    birthday, group/category, and type/phone_type.
    """
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
        email_col = headers.get("email")
        birthday_col = headers.get("birthday")
        group_col = headers.get("group") or headers.get("category")
        type_col = headers.get("phone_type") or headers.get("type")

        if not name_col or not phone_col:
            print("CSV must contain name and phone columns (or first_name and phone_number).")
            return

        for row_number, row in enumerate(reader, start=2):
            name = (row.get(name_col) or "").strip()
            if last_col:
                last_name = (row.get(last_col) or "").strip()
                if last_name:
                    name = f"{name} {last_name}".strip()
            phone = (row.get(phone_col) or "").strip()
            email = (row.get(email_col) or "").strip() or None if email_col else None
            birthday_text = (row.get(birthday_col) or "").strip() if birthday_col else ""
            group_name = (row.get(group_col) or "").strip() if group_col else ""
            phone_type = ((row.get(type_col) or "mobile").strip().lower() if type_col else "mobile") or "mobile"

            if not name or not valid_phone(phone) or phone_type not in PHONE_TYPES:
                skipped += 1
                print(f"Skipped invalid CSV row {row_number}: {name!r}, {phone!r}, {phone_type!r}")
                continue

            try:
                birthday = normalize_birthday(birthday_text)
                with conn:
                    with conn.cursor() as cur:
                        group_id = get_group_id(cur, group_name)
                        cur.execute(
                            """
                            INSERT INTO contacts (name, phone, email, birthday, group_id)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                            RETURNING id;
                            """,
                            (name, phone, email, birthday, group_id),
                        )
                        result = cur.fetchone()
                        if result:
                            contact_id = result[0]
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                                (contact_id, phone, phone_type),
                            )
                            inserted += 1
                        else:
                            skipped += 1
            except (ValueError, psycopg2.Error) as exc:
                skipped += 1
                print(f"Skipped CSV row {row_number}: {exc}")

    print(f"CSV import finished. Inserted: {inserted}; skipped: {skipped}.")


def update_contact(conn):
    """Keep the legacy contacts.phone value and its mirrored phones row in sync."""
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
    new_name = input("New name (Enter to keep current): ").strip() or old_name
    new_phone = input("New main phone (Enter to keep current): ").strip() or old_phone
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
                if new_phone != old_phone:
                    cur.execute(
                        "SELECT 1 FROM phones WHERE contact_id = %s AND phone = %s;",
                        (contact_id, new_phone),
                    )
                    new_phone_exists = cur.fetchone() is not None
                    if new_phone_exists:
                        cur.execute(
                            "DELETE FROM phones WHERE contact_id = %s AND phone = %s;",
                            (contact_id, old_phone),
                        )
                    else:
                        cur.execute(
                            "UPDATE phones SET phone = %s WHERE contact_id = %s AND phone = %s;",
                            (new_phone, contact_id, old_phone),
                        )
                        if cur.rowcount == 0:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, 'mobile') "
                                "ON CONFLICT (contact_id, phone) DO NOTHING;",
                                (contact_id, new_phone),
                            )
        print("Contact updated.")
    except psycopg2.Error as exc:
        print(f"Could not update contact: {exc}")


def search_contacts_console(conn):
    """Use the new database function that searches all extended contact fields."""
    term = input("Search name, email, or any phone fragment: ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s);", (term,))
        rows = cur.fetchall()

    if not rows:
        print("No matching contacts found.")
        return

    print("\n--- SEARCH RESULTS ---")
    for contact_id, name, email, birthday, group_name, phones in rows:
        print(f"{contact_id}. {name}")
        print(f"   Phones: {', '.join(phones) if phones else '—'}")
        print(f"   Email: {email or '—'} | Birthday: {birthday or '—'} | Group: {group_name or '—'}")


def delete_contact(conn):
    """Reuse the original Practice 7 delete-by-name-or-phone interaction."""
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
        print("Related rows in phones are removed automatically by ON DELETE CASCADE.")
    else:
        print("Contact not found.")


def add_phone_console(conn):
    name = input("Contact full name: ").strip()
    phone = input("Additional phone: ").strip()
    phone_type = input("Type (home/work/mobile): ").strip().lower()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s);", (name, phone, phone_type))
        print("Phone number added.")
    except psycopg2.Error as exc:
        print(f"Could not add phone: {exc}")


def move_contact_console(conn):
    name = input("Contact full name: ").strip()
    group_name = input("New group name: ").strip()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s);", (name, group_name))
        print(f"Contact moved to group '{group_name}'.")
    except psycopg2.Error as exc:
        print(f"Could not move contact: {exc}")


def _fetch_enriched_by_ids(conn, ids):
    if not ids:
        return []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                c.id, c.name, c.email, c.birthday, g.name, c.created_at,
                COALESCE(
                    ARRAY(
                        SELECT p.phone || ' (' || p.type || ')'
                        FROM phones AS p
                        WHERE p.contact_id = c.id
                        ORDER BY p.id
                    ),
                    ARRAY[]::TEXT[]
                )
            FROM contacts AS c
            LEFT JOIN "groups" AS g ON g.id = c.group_id
            WHERE c.id = ANY(%s)
            ORDER BY ARRAY_POSITION(%s, c.id);
            """,
            (ids, ids),
        )
        return cur.fetchall()


def fetch_contact_page(conn, page_size, offset, group_filter, email_query, sort_choice):
    """Use Practice 8 pagination for the unfiltered default view; otherwise
    apply the selected filters/sort in SQL and page with LIMIT/OFFSET.
    """
    if not group_filter and not email_query and sort_choice == "4":
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM get_contacts_paginated(%s, %s);", (page_size, offset))
            ids = [row[0] for row in cur.fetchall()]
        return _fetch_enriched_by_ids(conn, ids)

    order_by_options = {
        "1": "c.name ASC, c.id ASC",
        "2": "c.birthday ASC NULLS LAST, c.name ASC, c.id ASC",
        "3": "c.created_at DESC, c.id DESC",
        "4": "c.id ASC",
    }
    order_by = order_by_options.get(sort_choice, order_by_options["1"])
    email_pattern = f"%{email_query}%" if email_query else None

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT
                c.id, c.name, c.email, c.birthday, g.name, c.created_at,
                COALESCE(
                    ARRAY(
                        SELECT p.phone || ' (' || p.type || ')'
                        FROM phones AS p
                        WHERE p.contact_id = c.id
                        ORDER BY p.id
                    ),
                    ARRAY[]::TEXT[]
                )
            FROM contacts AS c
            LEFT JOIN "groups" AS g ON g.id = c.group_id
            WHERE (%s::TEXT IS NULL OR LOWER(g.name) = LOWER(%s))
              AND (%s::TEXT IS NULL OR COALESCE(c.email, '') ILIKE %s)
            ORDER BY {order_by}
            LIMIT %s OFFSET %s;
            """,
            (group_filter or None, group_filter or None, email_pattern, email_pattern, page_size, offset),
        )
        return cur.fetchall()


def print_enriched_page(rows, page_number):
    print(f"\n--- CONTACTS | PAGE {page_number} ---")
    if not rows:
        print("No contacts on this page.")
        return
    for contact_id, name, email, birthday, group_name, created_at, phones in rows:
        print(f"\n{contact_id}. {name}")
        print(f"   Phones: {', '.join(phones) if phones else '—'}")
        print(f"   Email: {email or '—'} | Birthday: {birthday or '—'}")
        print(f"   Group: {group_name or '—'} | Added: {created_at}")


def browse_contacts(conn):
    """Group/email filters, sorting and next/prev/quit page navigation."""
    group_filter = input("Filter by group (Enter for all): ").strip()
    email_query = input("Email contains (Enter for all): ").strip()

    print("Sort by: 1) name  2) birthday  3) date added  4) Practice 8 default pagination (ID)")
    sort_choice = input("Choose sort [1]: ").strip() or "1"
    if sort_choice not in {"1", "2", "3", "4"}:
        print("Unknown sort option. Using name.")
        sort_choice = "1"

    size_text = input(f"Contacts per page [{PAGE_SIZE}]: ").strip()
    try:
        page_size = int(size_text) if size_text else PAGE_SIZE
        if not 1 <= page_size <= 50:
            raise ValueError
    except ValueError:
        print("Page size must be between 1 and 50. Using 5.")
        page_size = PAGE_SIZE

    page = 0
    while True:
        offset = page * page_size
        rows = fetch_contact_page(conn, page_size, offset, group_filter, email_query, sort_choice)
        if not rows and page > 0:
            print("No next page. Returning to the last available page.")
            page -= 1
            continue
        print_enriched_page(rows, page + 1)
        command = input("Type next / prev / quit: ").strip().lower()
        if command == "next":
            page += 1
        elif command == "prev":
            page = max(0, page - 1)
        elif command == "quit":
            break
        else:
            print("Use next, prev, or quit.")


def export_json(conn):
    """Export contacts with group metadata and every phone number to JSON."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.name, c.phone, c.email, c.birthday, c.created_at, g.name
            FROM contacts AS c
            LEFT JOIN "groups" AS g ON g.id = c.group_id
            ORDER BY c.id;
            """
        )
        contacts = cur.fetchall()
        cur.execute("SELECT contact_id, phone, type FROM phones ORDER BY contact_id, id;")
        phone_rows = cur.fetchall()

    phones_by_contact = {}
    for contact_id, phone, phone_type in phone_rows:
        phones_by_contact.setdefault(contact_id, []).append(
            {"phone": phone, "type": phone_type}
        )

    payload = {"contacts": []}
    for contact_id, name, legacy_phone, email, birthday, created_at, group_name in contacts:
        contact_phones = phones_by_contact.get(contact_id, [])
        # Preserve the current Practice 7/8 primary phone even if an older
        # stored procedure inserted/updated the legacy contacts.phone column.
        if legacy_phone and not any(item["phone"] == legacy_phone for item in contact_phones):
            contact_phones = [{"phone": legacy_phone, "type": "mobile"}] + contact_phones
        payload["contacts"].append(
            {
                "name": name,
                "email": email,
                "birthday": birthday.isoformat() if birthday else None,
                "group": group_name,
                "created_at": created_at.isoformat() if created_at else None,
                "phones": contact_phones,
            }
        )

    path_text = input(f"JSON output path [{JSON_PATH}]: ").strip()
    path = Path(path_text).expanduser() if path_text else JSON_PATH
    if not path.is_absolute():
        path = BASE_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    print(f"Exported {len(contacts)} contacts to {path}")


def _normalize_json_phones(value):
    if not isinstance(value, list) or not value:
        raise ValueError("Each imported contact must contain at least one phone in the phones list.")

    result = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Each phone must be an object with phone and type fields.")
        phone = str(item.get("phone", "")).strip()
        phone_type = str(item.get("type", "mobile")).strip().lower()
        if not valid_phone(phone):
            raise ValueError(f"Invalid phone number: {phone!r}")
        if phone_type not in PHONE_TYPES:
            raise ValueError(f"Invalid phone type: {phone_type!r}")
        result.append((phone, phone_type))
    return result


def import_json(conn):
    """Import JSON contacts; duplicates by case-insensitive name can be skipped or overwritten."""
    path_text = input(f"JSON input path [{JSON_PATH}]: ").strip()
    path = Path(path_text).expanduser() if path_text else JSON_PATH
    if not path.is_absolute():
        path = BASE_DIR / path
    if not path.exists():
        print(f"JSON file not found: {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read JSON: {exc}")
        return

    records = payload.get("contacts") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        print("JSON must contain a list of contacts or an object with a 'contacts' list.")
        return

    inserted = overwritten = skipped = 0
    for index, record in enumerate(records, start=1):
        try:
            if not isinstance(record, dict):
                raise ValueError("Contact entry must be a JSON object.")
            name = str(record.get("name", "")).strip()
            if not name:
                raise ValueError("Contact name is required.")
            email = str(record.get("email") or "").strip() or None
            birthday = normalize_birthday(record.get("birthday"))
            group_name = str(record.get("group") or "").strip()
            phones = _normalize_json_phones(record.get("phones"))
            primary_phone = phones[0][0]

            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM contacts WHERE LOWER(name) = LOWER(%s) LIMIT 1;",
                        (name,),
                    )
                    existing = cur.fetchone()
                    if existing:
                        action = input(
                            f"Contact '{name}' already exists. Skip or overwrite? [s/o]: "
                        ).strip().lower()
                        if action not in {"o", "overwrite"}:
                            skipped += 1
                            continue
                        contact_id = existing[0]
                        group_id = get_group_id(cur, group_name)
                        cur.execute(
                            """
                            UPDATE contacts
                            SET phone = %s, email = %s, birthday = %s, group_id = %s
                            WHERE id = %s;
                            """,
                            (primary_phone, email, birthday, group_id, contact_id),
                        )
                        cur.execute("DELETE FROM phones WHERE contact_id = %s;", (contact_id,))
                        for phone, phone_type in phones:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                                (contact_id, phone, phone_type),
                            )
                        overwritten += 1
                    else:
                        group_id = get_group_id(cur, group_name)
                        cur.execute(
                            """
                            INSERT INTO contacts (name, phone, email, birthday, group_id)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING id;
                            """,
                            (name, primary_phone, email, birthday, group_id),
                        )
                        contact_id = cur.fetchone()[0]
                        for phone, phone_type in phones:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                                (contact_id, phone, phone_type),
                            )
                        inserted += 1
        except (ValueError, psycopg2.Error) as exc:
            skipped += 1
            print(f"Skipped JSON contact #{index}: {exc}")

    print(f"JSON import finished. Inserted: {inserted}; overwritten: {overwritten}; skipped: {skipped}.")


def main():
    conn = None
    try:
        conn = get_connection()
        print("Connected to Neon PostgreSQL.")
        check_schema(conn)
        print("TSIS 1 schema and database objects are ready.")

        while True:
            print("\n========== PHONEBOOK - TSIS 1 ==========")
            print("1. Show all contacts")
            print("2. Add contact (extended fields)")
            print("3. Import contacts from CSV (extended)")
            print("4. Update contact")
            print("5. Search contacts (name, email, all phones)")
            print("6. Delete contact")
            print("7. Browse: group/email filters, sorting, pagination")
            print("8. Export contacts to JSON")
            print("9. Import contacts from JSON")
            print("10. Add another phone number")
            print("11. Move contact to group")
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
                search_contacts_console(conn)
            elif choice == "6":
                delete_contact(conn)
            elif choice == "7":
                browse_contacts(conn)
            elif choice == "8":
                export_json(conn)
            elif choice == "9":
                import_json(conn)
            elif choice == "10":
                add_phone_console(conn)
            elif choice == "11":
                move_contact_console(conn)
            elif choice == "0":
                break
            else:
                print("Unknown option. Choose 0-11.")

    except Exception as exc:
        print(f"Application error: {exc}")
    finally:
        if conn is not None and not conn.closed:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
