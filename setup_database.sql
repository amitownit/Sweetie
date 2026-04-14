-- Run this in your Supabase SQL Editor (supabase.com → your project → SQL Editor)
-- It creates the table that stores all diabetes logs

CREATE TABLE IF NOT EXISTS diabetes_logs (
    id          BIGSERIAL PRIMARY KEY,
    phone       TEXT NOT NULL,
    user_message TEXT NOT NULL,
    bot_reply   TEXT NOT NULL,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Extracted health data (all optional)
    glucose     NUMERIC,          -- e.g. 142 or 7.8
    glucose_unit TEXT,            -- 'mg/dL' or 'mmol/L'
    meal        TEXT,             -- e.g. 'burger and fries'
    insulin     NUMERIC,          -- units of insulin taken
    mood        TEXT,             -- e.g. 'tired', 'dizzy', 'good'
    activity    TEXT,             -- e.g. 'basketball practice'
    notes       TEXT              -- anything else notable
);

-- Index for fast lookup by phone number
CREATE INDEX IF NOT EXISTS idx_diabetes_logs_phone ON diabetes_logs(phone);

-- Index for time-based queries (weekly reports etc.)
CREATE INDEX IF NOT EXISTS idx_diabetes_logs_timestamp ON diabetes_logs(timestamp);

-- Example query: Get all glucose readings for a user in the last 7 days
-- SELECT phone, glucose, glucose_unit, timestamp
-- FROM diabetes_logs
-- WHERE phone = '+31612345678'
--   AND glucose IS NOT NULL
--   AND timestamp > NOW() - INTERVAL '7 days'
-- ORDER BY timestamp ASC;
