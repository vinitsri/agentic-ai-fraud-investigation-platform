-- Phase 3: Rules engine alert payload columns

ALTER TABLE fraud_alerts ADD COLUMN IF NOT EXISTS fraud_score NUMERIC(5,4);
ALTER TABLE fraud_alerts ADD COLUMN IF NOT EXISTS triggered_rules JSONB;
ALTER TABLE fraud_alerts ADD COLUMN IF NOT EXISTS evidence JSONB;
