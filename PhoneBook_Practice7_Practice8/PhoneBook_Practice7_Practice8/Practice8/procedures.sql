-- Practice 8: PostgreSQL stored procedures

-- 1. Insert a new contact or update the phone for an existing name.
CREATE OR REPLACE PROCEDURE upsert_contact(
    IN p_name VARCHAR,
    IN p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_name IS NULL OR BTRIM(p_name) = '' THEN
        RAISE EXCEPTION 'Name cannot be empty';
    END IF;

    IF p_phone IS NULL OR BTRIM(p_phone) !~ '^\+?[0-9]{10,15}$' THEN
        RAISE EXCEPTION 'Invalid phone. Use 10-15 digits, optionally starting with +';
    END IF;

    IF EXISTS (
        SELECT 1 FROM contacts c
        WHERE LOWER(c.name) = LOWER(BTRIM(p_name))
    ) THEN
        UPDATE contacts
        SET phone = BTRIM(p_phone)
        WHERE LOWER(name) = LOWER(BTRIM(p_name));
    ELSE
        INSERT INTO contacts (name, phone)
        VALUES (BTRIM(p_name), BTRIM(p_phone));
    END IF;
END;
$$;

-- Test:
-- CALL upsert_contact('John Smith', '+77071112233');
-- CALL upsert_contact('John Smith', '+77074445566');

-- 2. Bulk insert. Valid rows are inserted; all invalid rows are returned
-- in the INOUT JSONB parameter. Both arrays must have equal length.
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    IN p_names TEXT[],
    IN p_phones TEXT[],
    INOUT p_invalid JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER;
    v_name TEXT;
    v_phone TEXT;
BEGIN
    p_invalid := '[]'::JSONB;

    IF COALESCE(array_length(p_names, 1), 0)
       <> COALESCE(array_length(p_phones, 1), 0) THEN
        p_invalid := jsonb_build_array(jsonb_build_object(
            'reason', 'Names and phones arrays must have the same length',
            'names_count', COALESCE(array_length(p_names, 1), 0),
            'phones_count', COALESCE(array_length(p_phones, 1), 0)
        ));
        RETURN;
    END IF;

    FOR i IN 1..COALESCE(array_length(p_names, 1), 0) LOOP
        v_name := p_names[i];
        v_phone := p_phones[i];

        IF v_name IS NULL OR BTRIM(v_name) = '' THEN
            p_invalid := p_invalid || jsonb_build_array(jsonb_build_object(
                'name', v_name, 'phone', v_phone, 'reason', 'Name is empty'
            ));
        ELSIF v_phone IS NULL OR BTRIM(v_phone) !~ '^\+?[0-9]{10,15}$' THEN
            p_invalid := p_invalid || jsonb_build_array(jsonb_build_object(
                'name', v_name, 'phone', v_phone, 'reason', 'Invalid phone format'
            ));
        ELSE
            BEGIN
                INSERT INTO contacts (name, phone)
                VALUES (BTRIM(v_name), BTRIM(v_phone));
            EXCEPTION WHEN unique_violation THEN
                p_invalid := p_invalid || jsonb_build_array(jsonb_build_object(
                    'name', v_name, 'phone', v_phone,
                    'reason', 'Name or phone already exists'
                ));
            END;
        END IF;
    END LOOP;
END;
$$;

-- Test. CALL returns one row containing the invalid JSON array:
-- CALL insert_many_contacts(
--   ARRAY['Alice Green', 'Bad Phone', 'Bob Stone'],
--   ARRAY['+77070000010', '12345', '+77070000011'],
--   NULL
-- );

-- 3. Delete by exactly one identifier: name OR phone.
CREATE OR REPLACE PROCEDURE delete_contact(
    IN p_name TEXT DEFAULT NULL,
    IN p_phone TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    IF (p_name IS NULL AND p_phone IS NULL)
       OR (p_name IS NOT NULL AND p_phone IS NOT NULL) THEN
        RAISE EXCEPTION 'Provide either a name or a phone number, but not both';
    END IF;

    IF p_name IS NOT NULL THEN
        DELETE FROM contacts
        WHERE LOWER(name) = LOWER(BTRIM(p_name));
    ELSE
        DELETE FROM contacts
        WHERE phone = BTRIM(p_phone);
    END IF;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % contact(s)', deleted_count;
END;
$$;

-- Tests:
-- CALL delete_contact('John Smith', NULL);
-- CALL delete_contact(NULL, '+77071112233');
