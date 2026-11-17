-- TSIS 1: PhoneBook extended schema
-- Run this AFTER Practice 7 has created the original contacts table.
-- This is an additive, repeatable migration: it preserves Practice 7-8 objects.

CREATE TABLE IF NOT EXISTS "groups" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO "groups" (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

ALTER TABLE contacts
    ADD COLUMN IF NOT EXISTS email VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday DATE,
    ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES "groups"(id) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) NOT NULL DEFAULT 'mobile'
        CHECK (type IN ('home', 'work', 'mobile')),
    CONSTRAINT phones_contact_phone_unique UNIQUE (contact_id, phone)
);

-- Migrate each old Practice 7 phone into the new one-to-many phones table.
-- The old contacts.phone column is intentionally kept for compatibility
-- with the Practice 7-8 functions and procedures.
INSERT INTO phones (contact_id, phone, type)
SELECT id, phone, 'mobile'
FROM contacts
WHERE phone IS NOT NULL AND BTRIM(phone) <> ''
ON CONFLICT (contact_id, phone) DO NOTHING;

CREATE INDEX IF NOT EXISTS phones_contact_id_idx ON phones(contact_id);
CREATE INDEX IF NOT EXISTS contacts_group_id_idx ON contacts(group_id);
CREATE INDEX IF NOT EXISTS contacts_email_lower_idx ON contacts(LOWER(email));
