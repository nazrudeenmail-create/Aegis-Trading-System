-- Aegis Trading System — PostgreSQL Initialization Script
--
-- This file runs automatically when the PostgreSQL container starts for the first time.
-- The ats_development database and ats_user are created by Docker environment variables:
--   POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
--
-- This script handles additional setup that environment variables cannot do.

-- Enable UUID generation extension
-- Used by ATS for primary keys on all tables (Phase 2)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable additional statistical functions (useful for performance analysis in Phase 13)
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
