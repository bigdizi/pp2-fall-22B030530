-- Run these after schema.sql and procedures.sql in Neon SQL Editor.

-- 1. Confirm default groups exist.
SELECT * FROM "groups" ORDER BY id;

-- 2. Confirm old Practice 7 phone values were migrated.
SELECT c.id, c.name, p.phone, p.type
FROM contacts AS c
JOIN phones AS p ON p.contact_id = c.id
ORDER BY c.id, p.id;

-- 3. Add a second phone to an existing contact (replace the name if needed).
-- CALL add_phone('Johnny', '+77070000123', 'work');

-- 4. Move a contact to an existing or newly-created group.
-- CALL move_to_group('Johnny', 'Family');

-- 5. Search by name, email, legacy phone, or any additional phone.
SELECT * FROM search_contacts('gmail');
SELECT * FROM search_contacts('7707');
SELECT * FROM search_contacts('John');

-- 6. Existing Practice 8 pagination function remains available.
SELECT * FROM get_contacts_paginated(5, 0);

-- 7. Inspect all phones for each contact.
SELECT c.name, p.phone, p.type
FROM contacts AS c
LEFT JOIN phones AS p ON p.contact_id = c.id
ORDER BY c.name, p.id;
