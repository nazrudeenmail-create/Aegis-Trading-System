-- Create a read-only/limited development user for Codespaces
-- Run this script using:
-- docker compose exec -T postgres psql -U ats_user -d ats_development < scripts/create_dev_user.sql

-- 1. Create the user
CREATE ROLE ats_dev WITH LOGIN PASSWORD 'ats_dev_password';

-- 2. Grant connection rights
GRANT CONNECT ON DATABASE ats_development TO ats_dev;

-- 3. Grant usage on the public schema
GRANT USAGE ON SCHEMA public TO ats_dev;

-- 4. Grant SELECT on all existing tables (like candles, instruments)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ats_dev;

-- 5. Set default privileges so future tables are also readable
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ats_dev;

-- Note: If you want to allow the dev user to create temporary tables or write to specific
-- development-only tables, you can add those explicit GRANTs here.
-- Example:
-- GRANT ALL PRIVILEGES ON TABLE public.indicator_state TO ats_dev;
