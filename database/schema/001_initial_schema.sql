-- ============================================================
-- Agentic AI Fraud Investigation Platform
-- Phase 2: Core Data Model
-- ============================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ── Enums ───────────────────────────────────────────────────

CREATE TYPE account_status AS ENUM ('ACTIVE', 'SUSPENDED', 'CLOSED');
CREATE TYPE transaction_status AS ENUM ('PENDING', 'COMPLETED', 'DECLINED', 'REVERSED');
CREATE TYPE alert_status AS ENUM ('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE');
CREATE TYPE alert_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE fraud_case_status AS ENUM ('OPEN', 'CONFIRMED', 'DISMISSED', 'ESCALATED');
CREATE TYPE investigation_status AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED');
CREATE TYPE agent_run_status AS ENUM ('RUNNING', 'COMPLETED', 'FAILED', 'TIMEOUT');
CREATE TYPE analyst_action AS ENUM (
    'CONFIRM_FRAUD', 'FALSE_POSITIVE', 'APPROVE',
    'ESCALATE', 'REQUEST_INFO'
);
CREATE TYPE recommendation_type AS ENUM ('APPROVE', 'MANUAL_REVIEW', 'BLOCK');

-- ── Merchants ───────────────────────────────────────────────

CREATE TABLE merchants (
    merchant_id     VARCHAR(36)  PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    category_code   VARCHAR(10)  NOT NULL,
    category_name   VARCHAR(100) NOT NULL,
    risk_score      NUMERIC(5,4) NOT NULL DEFAULT 0.0
                    CHECK (risk_score BETWEEN 0 AND 1),
    country         CHAR(2)      NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_merchants_category ON merchants(category_code);
CREATE INDEX idx_merchants_risk ON merchants(risk_score);

-- ── Customers ───────────────────────────────────────────────

CREATE TABLE customers (
    customer_id         VARCHAR(36)  PRIMARY KEY,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255) NOT NULL UNIQUE,
    phone               VARCHAR(20),
    date_of_birth       DATE         NOT NULL,
    account_status      account_status NOT NULL DEFAULT 'ACTIVE',
    account_created_at  TIMESTAMPTZ  NOT NULL,
    home_country        CHAR(2)      NOT NULL,
    home_city           VARCHAR(100) NOT NULL,
    home_latitude       NUMERIC(9,6),
    home_longitude      NUMERIC(9,6),
    avg_transaction_amt NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_customers_status ON customers(account_status);
CREATE INDEX idx_customers_country ON customers(home_country);

-- ── Devices ─────────────────────────────────────────────────

CREATE TABLE devices (
    device_id       VARCHAR(36)  PRIMARY KEY,
    device_type     VARCHAR(50)  NOT NULL,
    os              VARCHAR(50)  NOT NULL,
    browser         VARCHAR(50),
    fingerprint_hash VARCHAR(64) NOT NULL,
    first_seen_at   TIMESTAMPTZ  NOT NULL,
    last_seen_at    TIMESTAMPTZ  NOT NULL,
    is_trusted      BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_devices_fingerprint ON devices(fingerprint_hash);

-- ── Customer ↔ Device (many-to-many) ────────────────────────

CREATE TABLE customer_devices (
    customer_id     VARCHAR(36) NOT NULL REFERENCES customers(customer_id),
    device_id       VARCHAR(36) NOT NULL REFERENCES devices(device_id),
    first_associated_at TIMESTAMPTZ NOT NULL,
    last_used_at    TIMESTAMPTZ NOT NULL,
    is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (customer_id, device_id)
);

-- ── Transactions ────────────────────────────────────────────

CREATE TABLE transactions (
    transaction_id      VARCHAR(36)  PRIMARY KEY,
    customer_id         VARCHAR(36)  NOT NULL REFERENCES customers(customer_id),
    merchant_id         VARCHAR(36)  NOT NULL REFERENCES merchants(merchant_id),
    device_id           VARCHAR(36)  REFERENCES devices(device_id),
    amount              NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    currency            CHAR(3)      NOT NULL DEFAULT 'USD',
    status              transaction_status NOT NULL DEFAULT 'COMPLETED',
    transaction_type    VARCHAR(50)  NOT NULL,
    merchant_category   VARCHAR(10)  NOT NULL,
    ip_address          INET,
    latitude            NUMERIC(9,6),
    longitude           NUMERIC(9,6),
    city                VARCHAR(100),
    country             CHAR(2),
    is_fraud            BOOLEAN      NOT NULL DEFAULT FALSE,
    fraud_scenario      VARCHAR(50),
    created_at          TIMESTAMPTZ  NOT NULL
);

CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_merchant ON transactions(merchant_id);
CREATE INDEX idx_transactions_device ON transactions(device_id);
CREATE INDEX idx_transactions_created ON transactions(created_at);
CREATE INDEX idx_transactions_fraud ON transactions(is_fraud) WHERE is_fraud = TRUE;
CREATE INDEX idx_transactions_customer_created ON transactions(customer_id, created_at DESC);

-- ── Login Events ────────────────────────────────────────────

CREATE TABLE login_events (
    login_id        VARCHAR(36)  PRIMARY KEY,
    customer_id     VARCHAR(36)  NOT NULL REFERENCES customers(customer_id),
    device_id       VARCHAR(36)  REFERENCES devices(device_id),
    ip_address      INET         NOT NULL,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    city            VARCHAR(100),
    country         CHAR(2),
    success         BOOLEAN      NOT NULL,
    failure_reason  VARCHAR(100),
    created_at      TIMESTAMPTZ  NOT NULL
);

CREATE INDEX idx_login_events_customer ON login_events(customer_id);
CREATE INDEX idx_login_events_created ON login_events(created_at);
CREATE INDEX idx_login_events_failed ON login_events(customer_id, success)
    WHERE success = FALSE;

-- ── Fraud Alerts ────────────────────────────────────────────

CREATE TABLE fraud_alerts (
    alert_id            VARCHAR(36)  PRIMARY KEY,
    transaction_id      VARCHAR(36)  NOT NULL REFERENCES transactions(transaction_id),
    customer_id         VARCHAR(36)  NOT NULL REFERENCES customers(customer_id),
    status              alert_status NOT NULL DEFAULT 'OPEN',
    severity            alert_severity NOT NULL,
    rule_triggered      VARCHAR(100),
    fraud_score         NUMERIC(5,4),
    triggered_rules     JSONB,
    evidence            JSONB,
    ml_fraud_probability NUMERIC(5,4),
    triggered_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fraud_alerts_status ON fraud_alerts(status);
CREATE INDEX idx_fraud_alerts_customer ON fraud_alerts(customer_id);
CREATE INDEX idx_fraud_alerts_transaction ON fraud_alerts(transaction_id);

-- ── Fraud Cases (historical, for RAG in Phase 9) ────────────

CREATE TABLE fraud_cases (
    case_id             VARCHAR(36)  PRIMARY KEY,
    customer_id         VARCHAR(36)  REFERENCES customers(customer_id),
    title               VARCHAR(255) NOT NULL,
    description         TEXT         NOT NULL,
    fraud_type          VARCHAR(50)  NOT NULL,
    status              fraud_case_status NOT NULL DEFAULT 'OPEN',
    total_loss_amount   NUMERIC(12,2),
    currency            CHAR(3)      DEFAULT 'USD',
    resolution_notes    TEXT,
    detected_at         TIMESTAMPTZ  NOT NULL,
    resolved_at         TIMESTAMPTZ,
    embedding           vector(384),
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fraud_cases_type ON fraud_cases(fraud_type);
CREATE INDEX idx_fraud_cases_status ON fraud_cases(status);

-- ── Investigation Reports (Phase 6+, schema now) ───────────

CREATE TABLE investigation_reports (
    report_id           VARCHAR(36)  PRIMARY KEY,
    alert_id            VARCHAR(36)  NOT NULL REFERENCES fraud_alerts(alert_id),
    status              investigation_status NOT NULL DEFAULT 'PENDING',
    risk_level          alert_severity,
    confidence          NUMERIC(5,4),
    recommendation      recommendation_type,
    risk_factors        JSONB,
    evidence            JSONB,
    similar_cases       JSONB,
    summary             TEXT,
    prompt_version      VARCHAR(20),
    model_used          VARCHAR(100),
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_investigation_reports_alert ON investigation_reports(alert_id);
CREATE INDEX idx_investigation_reports_status ON investigation_reports(status);

-- ── Agent Runs (Phase 6+, schema now) ───────────────────────

CREATE TABLE agent_runs (
    run_id              VARCHAR(36)  PRIMARY KEY,
    alert_id            VARCHAR(36)  NOT NULL REFERENCES fraud_alerts(alert_id),
    agent_name          VARCHAR(100) NOT NULL,
    status              agent_run_status NOT NULL DEFAULT 'RUNNING',
    prompt_version      VARCHAR(20),
    model_used          VARCHAR(100),
    tools_called        JSONB,
    retrieved_documents JSONB,
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    latency_ms          INTEGER,
    result              JSONB,
    error_message       TEXT,
    trace_id            VARCHAR(64),
    started_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ
);

CREATE INDEX idx_agent_runs_alert ON agent_runs(alert_id);
CREATE INDEX idx_agent_runs_agent ON agent_runs(agent_name);
CREATE INDEX idx_agent_runs_trace ON agent_runs(trace_id);

-- ── Analyst Decisions (Phase 12+, schema now) ───────────────

CREATE TABLE analyst_decisions (
    decision_id         VARCHAR(36)  PRIMARY KEY,
    alert_id            VARCHAR(36)  NOT NULL REFERENCES fraud_alerts(alert_id),
    report_id           VARCHAR(36)  REFERENCES investigation_reports(report_id),
    analyst_id          VARCHAR(36)  NOT NULL,
    action              analyst_action NOT NULL,
    notes               TEXT,
    override_recommendation recommendation_type,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analyst_decisions_alert ON analyst_decisions(alert_id);
CREATE INDEX idx_analyst_decisions_analyst ON analyst_decisions(analyst_id);
