CREATE DATABASE interview;CREATE TABLE IF NOT EXISTS app_user (
    id BIGINT PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO app_user (id, phone, hashed_password, is_superuser, created_at, updated_at)
VALUES (
    100000,
    '12345678901',
    'test_hashed_password',
    FALSE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);