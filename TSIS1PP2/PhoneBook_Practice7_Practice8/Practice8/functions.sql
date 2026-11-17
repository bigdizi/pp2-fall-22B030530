-- Practice 8: PostgreSQL functions

-- 1. Search by part of full name or phone number.
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE (id INTEGER, name VARCHAR, phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.phone
    FROM contacts AS c
    WHERE c.name ILIKE '%' || COALESCE(p_pattern, '') || '%'
       OR c.phone ILIKE '%' || COALESCE(p_pattern, '') || '%'
    ORDER BY c.id;
END;
$$;

-- Test:
-- SELECT * FROM get_contacts_by_pattern('john');
-- SELECT * FROM get_contacts_by_pattern('7707');

-- 2. Pagination. p_limit = page size; p_offset = rows to skip.
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (id INTEGER, name VARCHAR, phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_limit IS NULL OR p_limit < 1 OR p_limit > 100 THEN
        RAISE EXCEPTION 'Limit must be between 1 and 100';
    END IF;

    IF p_offset IS NULL OR p_offset < 0 THEN
        RAISE EXCEPTION 'Offset cannot be negative';
    END IF;

    RETURN QUERY
    SELECT c.id, c.name, c.phone
    FROM contacts AS c
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$;

-- Test first page (10 rows):
-- SELECT * FROM get_contacts_paginated(10, 0);
-- Test second page (10 rows):
-- SELECT * FROM get_contacts_paginated(10, 10);
