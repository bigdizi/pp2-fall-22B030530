# Practice 8 - Functions & Stored Procedures

Run `functions.sql` and `procedures.sql` in the Neon SQL Editor after Practice 7 has created the `contacts` table.

Required objects:
- Functions: `get_contacts_by_pattern`, `get_contacts_paginated`
- Procedures: `upsert_contact`, `insert_many_contacts`, `delete_contact`

Test commands are included as SQL comments at the bottom of each file. For the bulk procedure, execute the sample `CALL` and inspect the returned `p_invalid` JSONB value for rejected rows.
