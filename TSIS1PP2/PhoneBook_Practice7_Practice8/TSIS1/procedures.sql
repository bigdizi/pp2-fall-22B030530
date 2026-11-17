-- TSIS 1: New database-side objects only.
-- Existing Practice 8 objects are not recreated here.

-- 1. Add an additional phone number to an existing contact.
CREATE OR REPLACE PROCEDURE add_phone(
    IN p_contact_name VARCHAR,
    IN p_phone VARCHAR,
    IN p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_type VARCHAR(10);
BEGIN
    IF p_contact_name IS NULL OR BTRIM(p_contact_name) = '' THEN
        RAISE EXCEPTION 'Contact name cannot be empty';
    END IF;

    IF p_phone IS NULL OR BTRIM(p_phone) !~ '^\+?[0-9]{10,15}$' THEN
        RAISE EXCEPTION 'Invalid phone. Use 10-15 digits, optionally starting with +';
    END IF;

    v_type := LOWER(BTRIM(COALESCE(p_type, '')));
    IF v_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Phone type must be home, work, or mobile';
    END IF;

    SELECT id
    INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(BTRIM(p_contact_name));

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact not found: %', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, BTRIM(p_phone), v_type)
    ON CONFLICT (contact_id, phone)
    DO UPDATE SET type = EXCLUDED.type;
END;
$$;

-- 2. Move a contact to an existing group or create the group when necessary.
CREATE OR REPLACE PROCEDURE move_to_group(
    IN p_contact_name VARCHAR,
    IN p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
BEGIN
    IF p_contact_name IS NULL OR BTRIM(p_contact_name) = '' THEN
        RAISE EXCEPTION 'Contact name cannot be empty';
    END IF;

    IF p_group_name IS NULL OR BTRIM(p_group_name) = '' THEN
        RAISE EXCEPTION 'Group name cannot be empty';
    END IF;

    SELECT id
    INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(BTRIM(p_contact_name));

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact not found: %', p_contact_name;
    END IF;

    SELECT id
    INTO v_group_id
    FROM "groups"
    WHERE LOWER(name) = LOWER(BTRIM(p_group_name));

    IF NOT FOUND THEN
        INSERT INTO "groups" (name)
        VALUES (BTRIM(p_group_name))
        RETURNING id INTO v_group_id;
    END IF;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;
END;
$$;

-- 3. Extended search: contact name, legacy phone, email, and every phone
-- stored in the new phones table. One result row is returned per contact.
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR(100),
    email VARCHAR(100),
    birthday DATE,
    group_name VARCHAR(50),
    phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pattern TEXT := '%' || COALESCE(p_query, '') || '%';
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name,
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
    WHERE c.name ILIKE v_pattern
       OR COALESCE(c.phone, '') ILIKE v_pattern
       OR COALESCE(c.email, '') ILIKE v_pattern
       OR EXISTS (
            SELECT 1
            FROM phones AS p
            WHERE p.contact_id = c.id
              AND p.phone ILIKE v_pattern
       )
    ORDER BY c.id;
END;
$$;

-- Example tests:
-- CALL add_phone('Johnny', '+77070000010', 'work');
-- CALL move_to_group('Johnny', 'Family');
-- SELECT * FROM search_contacts('gmail');
-- SELECT * FROM search_contacts('7707');
-- SELECT * FROM search_contacts('John');
