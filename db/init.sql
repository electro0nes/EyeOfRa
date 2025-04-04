CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    platform TEXT,
    handle TEXT,
    name TEXT,
    data JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uniq_platform_handle ON programs(platform, handle);