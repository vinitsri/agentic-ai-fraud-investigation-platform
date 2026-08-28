CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE alert_status AS ENUM ('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE');
CREATE TYPE alert_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE transaction_status AS ENUM ('PENDING', 'COMPLETED', 'DECLINED', 'REVERSED');
CREATE TYPE account_status AS ENUM ('ACTIVE', 'SUSPENDED', 'CLOSED');

CREATE TABLE merchants (
    merchant_id     VARCHAR(36)  PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    category_code   VARCHAR(10)  NOT NULL,
    category_name   VARCHAR(100) NOT NULL,
    risk_score      NUMERIC(5,4) NOT NULL DEFAULT 0.0,
    country         CHAR(2)      NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

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

CREATE TABLE customer_devices (
    customer_id     VARCHAR(36) NOT NULL REFERENCES customers(customer_id),
    device_id       VARCHAR(36) NOT NULL REFERENCES devices(device_id),
    first_associated_at TIMESTAMPTZ NOT NULL,
    last_used_at    TIMESTAMPTZ NOT NULL,
    is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (customer_id, device_id)
);

CREATE TABLE transactions (
    transaction_id      VARCHAR(36)  PRIMARY KEY,
    customer_id         VARCHAR(36)  NOT NULL REFERENCES customers(customer_id),
    merchant_id         VARCHAR(36)  NOT NULL REFERENCES merchants(merchant_id),
    device_id           VARCHAR(36)  REFERENCES devices(device_id),
    amount              NUMERIC(12,2) NOT NULL,
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
