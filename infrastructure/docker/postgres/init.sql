-- Enable pgvector extension (Phase 9 will use this)
CREATE EXTENSION IF NOT EXISTS vector;

-- Apply core schema (Phase 2)
\i /docker-entrypoint-initdb.d/schema/001_initial_schema.sql

DO $$
BEGIN
  RAISE NOTICE 'Fraud Investigation Platform - PostgreSQL initialized';
END $$;
