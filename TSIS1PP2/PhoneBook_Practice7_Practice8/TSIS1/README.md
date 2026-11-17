# TSIS 1 - Extended PhoneBook

This folder extends the existing Practice 7 and Practice 8 PhoneBook project. It does not recreate the Practice 7-8 functions and procedures.

## What is reused

- Practice 7 `contacts` table and CRUD workflow
- Practice 7 CSV import, extended to accept the TSIS 1 fields
- Practice 8 `get_contacts_paginated()` for the default ID-ordered page view
- Practice 8 database connection approach (`psycopg2` + Neon)

The old `contacts.phone` column is intentionally retained because Practice 7-8 SQL objects use it. The migration copies every existing `contacts.phone` value into the new `phones` table as a `mobile` number. New additional phone numbers are stored in `phones`.

## New TSIS 1 features

- `groups` table with the initial Family, Work, Friend, and Other groups
- `email`, `birthday`, and `group_id` columns on `contacts`
- `phones` table with a one-to-many relationship and `home`, `work`, `mobile` types
- Console filtering by group and partial email search
- Sorting by name, birthday, or date added
- `next` / `prev` / `quit` page navigation
- JSON export and JSON import with skip/overwrite handling for duplicate names
- Extended CSV import with email, birthday, group, and phone type
- New `add_phone` and `move_to_group` procedures
- New `search_contacts` function, searching name, email, legacy phone, and all rows in `phones`

## Setup (Neon)

1. Make sure Practice 7 and Practice 8 are already installed and working.
2. In Neon SQL Editor, run `schema.sql` from this folder. It is an additive migration and preserves the existing Practice 7-8 objects.
3. Run `procedures.sql` from this folder.
4. Create `TSIS1/.env` by copying `.env.example` and adding your Neon connection string. The application also checks `Practice7/.env` as a fallback.
5. Install dependencies if needed:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Start the extended application:

   ```bash
   python phonebook.py
   ```

## CSV format

The CSV importer accepts these columns:

```csv
name,phone,email,birthday,group,phone_type
Alice Brown,+77070000101,alice@gmail.com,2001-04-12,Family,mobile
```

`name` and `phone` are required. `email`, `birthday`, `group`, and `phone_type` are optional. Birthday must use `YYYY-MM-DD`. Phone type must be `home`, `work`, or `mobile`.

The original Practice 7 CSV format `name,phone` is still supported.

## JSON format

The exporter creates a JSON object with a `contacts` array. Each contact includes `name`, `email`, `birthday`, `group`, `created_at`, and a `phones` array containing objects with `phone` and `type`.

For import, every new contact must have at least one valid phone because the original Practice 7 `contacts.phone` column is still NOT NULL and UNIQUE. When a name already exists (case-insensitive match), the program asks whether to skip or overwrite it.

## Suggested TSIS 1 demonstration

1. Show that old contacts were migrated to `phones`.
2. Add another phone with option 10.
3. Move a contact into a group with option 11.
4. Search for a partial email or a secondary phone with option 5.
5. Browse and demonstrate filters, sorting, and next/prev navigation with option 7.
6. Export JSON with option 8, then import it with option 9 and demonstrate duplicate handling.
7. Run `SELECT * FROM search_contacts('gmail');` in Neon to show the database-side function.

## Important

Do not upload `.env` to GitHub. Run the SQL migration before launching the TSIS 1 application.
