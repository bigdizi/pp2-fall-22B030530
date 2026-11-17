# TSIS 1 - Short Defense Guide

Use these explanations in your own words. The project extends Practice 7 and Practice 8 rather than recreating their features.

## 1. What changed in the database?

**Answer:** I extended the existing `contacts` table with `email`, `birthday`, and `group_id`. I added a `groups` table and a separate `phones` table. A contact can now have multiple phone numbers, and each phone has a type: `home`, `work`, or `mobile`.

**Why a separate phones table?** It is a one-to-many relationship. One contact can have many phone records. If I stored phone1, phone2, phone3 as columns in contacts, the design would be harder to extend and normalize.

**Why is there a foreign key?** `phones.contact_id` references `contacts.id`, so every phone belongs to an existing contact. `ON DELETE CASCADE` removes the related phone rows when the contact is deleted.

**Why keep `contacts.phone`?** Practice 7 and Practice 8 already use that column. I kept it for backward compatibility and copied the existing values into `phones` during migration. The extended search also checks this legacy column.

## 2. What does schema.sql do?

- Creates the `groups` table and inserts Family, Work, Friend, and Other if they are missing.
- Adds `email`, `birthday`, and `group_id` to the existing contacts table.
- Creates `phones` with a foreign key and a CHECK constraint for the three allowed phone types.
- Copies old `contacts.phone` values into `phones` as mobile numbers.
- Adds indexes to make common lookups more efficient.

It is an additive migration. It does not drop the original table or remove Practice 8 objects.

## 3. What does add_phone do?

`add_phone(p_contact_name, p_phone, p_type)` validates the contact name, phone format, and phone type. It finds the contact ID by name and inserts the new phone into `phones`. It raises an exception when the contact does not exist or the phone/type is invalid.

## 4. What does move_to_group do?

`move_to_group(p_contact_name, p_group_name)` finds the contact, searches for the group, creates the group if it does not exist, and updates `contacts.group_id`.

## 5. What does search_contacts do?

It searches for the query in the contact name, email, the legacy phone column, and all phone numbers in `phones`. `ILIKE` performs a case-insensitive pattern match. `EXISTS` checks whether at least one associated phone matches without duplicating the contact in the results. The result includes the contact's group and an array of phone numbers with their types.

## 6. How do filters and sorting work?

The console asks for an optional group and an optional email fragment. Group filtering uses the selected group; email filtering uses `ILIKE` with `%query%`. Sort options are selected from a fixed whitelist: name, birthday, or `created_at` (date added). The SQL order-by fragment is never taken directly from user input.

## 7. How is pagination implemented?

The project reuses the Practice 8 `get_contacts_paginated(limit, offset)` function for the unfiltered ID-ordered page view. The console loop changes the offset with `next` and `prev`, and exits with `quit`. For filtered or custom-sorted pages, the app applies the same LIMIT/OFFSET idea to the filtered SQL query.

## 8. How does JSON export work?

The program reads each contact, its group, and all associated phone records, builds Python dictionaries/lists, and writes them with `json.dump()`. Birthday and date-added values are converted to ISO strings. The export includes every phone and its type.

## 9. How does JSON import handle duplicates?

The program reads the JSON file with `json.load()`. It checks whether a contact with the same name already exists, ignoring letter case. The user can skip it or overwrite its email, birthday, group, and phone list. Each contact is processed inside a database transaction, so a failed contact import is rolled back without leaving a partially updated contact.

## 10. How was CSV import extended?

The original importer still accepts `name,phone`. It also recognizes optional `email`, `birthday`, `group`, and `phone_type` (or `type`) fields. It validates phone numbers, birthday format, and phone type before inserting a contact and its phone record.

## 11. Where are parameterized queries used?

User-provided values are passed separately to `cursor.execute()` using `%s` placeholders. This avoids building SQL by concatenating input strings and helps prevent SQL injection. The only dynamic ORDER BY fragments come from a fixed internal dictionary.

## 12. How are transactions handled?

The app uses `with conn:` blocks around write operations. A successful block commits; an exception causes rollback. This keeps related writes together. For example, creating a contact and inserting its first phone should succeed or fail as one unit.

## Suggested live demo

1. Show current contacts and the migrated phone records.
2. Add an additional phone to an existing contact.
3. Move that contact into Family or a new group.
4. Search by a partial email fragment or by the additional phone number.
5. Browse contacts filtered by group and sorted by birthday.
6. Export JSON, then import it and show the skip/overwrite prompt.
7. In Neon SQL Editor, run `SELECT * FROM search_contacts('gmail');`.
