# PhoneBook - Practice 7, Practice 8, and TSIS 1

- `Practice7/` contains the original CRUD console application and Neon connection setup.
- `Practice8/` contains the existing pattern-search/pagination functions and upsert, bulk-insert, and delete procedures.
- `TSIS1/` extends that same project with multiple phone numbers, email, birthday, groups, filtered/sorted pagination, JSON import/export, and three new database-side objects.

Run Practice 7 first, then Practice 8 SQL, then `TSIS1/schema.sql`, then `TSIS1/procedures.sql`. See `TSIS1/README.md` for details.

Keep the real `.env` file out of GitHub. The TSIS 1 app can reuse `Practice7/.env` or use its own `TSIS1/.env`.
