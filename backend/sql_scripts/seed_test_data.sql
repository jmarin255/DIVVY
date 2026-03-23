-- Seed test data for users, groups, and group_memberships
-- Run after create_tables.sql

BEGIN;

TRUNCATE TABLE refresh_sessions, group_memberships, groups, users RESTART IDENTITY CASCADE;

INSERT INTO users (first_name, last_name, email, phone, password_hash)
VALUES
    ('Ava', 'Nguyen', 'ava.nguyen@example.com', '385-555-1001', '$2b$12$examplehashvalueforava000000000000000000000000000000'),
    ('Liam', 'Carter', 'liam.carter@example.com', '385-555-1002', '$2b$12$examplehashvalueforliam0000000000000000000000000000'),
    ('Mia', 'Patel', 'mia.patel@example.com', '385-555-1003', '$2b$12$examplehashvalueformia000000000000000000000000000000'),
    ('Noah', 'Kim', 'noah.kim@example.com', NULL, '$2b$12$examplehashvaluefornoah00000000000000000000000000000'),
    ('Sofia', 'Reed', 'sofia.reed@example.com', '385-555-1005', '$2b$12$examplehashvalueforsofia000000000000000000000000000'),
    ('Ethan', 'Brooks', 'ethan.brooks@example.com', '385-555-1006', '$2b$12$examplehashvalueforethan000000000000000000000000000');

INSERT INTO groups (name, join_code)
VALUES
    ('Apartment 2B', 'APT2B'),
    ('Summer Road Trip', 'TR1P9'),
    ('House Utilities', 'UTIL5');

INSERT INTO group_memberships (user_id, group_id, role)
VALUES
    (1, 1, 'owner'),
    (3, 1, 'member'),
    (4, 1, 'member'),

    (2, 2, 'owner'),
    (1, 2, 'member'),
    (6, 2, 'member'),

    (5, 3, 'owner'),
    (2, 3, 'member'),
    (3, 3, 'member');

COMMIT;
