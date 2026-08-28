# Deterministic Rules vs LLM Reasoning

Phase 3 introduces a **deterministic fraud rules engine** in the Spring Boot `fraud-service`. Phase 5+ adds LLM-based investigation agents. These layers are intentionally separate.

## Why keep rules separate from the LLM?

### 1. Predictability and auditability

Deterministic rules produce the same output for the same inputs. Every alert includes:

- Exact rules triggered
- Numerical fraud score
- Structured evidence objects

Regulators, auditors, and fraud analysts can replay decisions without non-deterministic model variance.

### 2. Separation of detection and explanation

| Layer | Role | Phase |
|-------|------|-------|
| Rules engine | **Detect** suspicious patterns | 3 |
| ML model | **Score** behavioral risk probabilistically | 4 |
| LLM agents | **Investigate and explain** alerts | 6+ |

The LLM never replaces the rules engine. It receives alerts and gathers evidence through tools.

### 3. Safety and policy control

Business policies (block, manual review, approve) must remain under deterministic control. LLMs can hallucinate, misinterpret context, or be prompt-injected. Rules enforce hard thresholds before any generative reasoning occurs.

### 4. Latency and cost

Rule evaluation runs in milliseconds against PostgreSQL. LLM investigation is slower and resource-intensive. Fast, cheap screening filters the transaction stream; agents focus only on flagged alerts.

### 5. Testability

Each rule has unit tests with fixed inputs and expected outputs. LLM behavior requires separate evaluation frameworks (Phase 14) with mocked models.

## Architecture

```
Transaction
    │
    ▼
Rules Engine (deterministic) ──► fraud_score + triggered_rules + evidence
    │
    ▼
Fraud Alert (PostgreSQL)
    │
    ▼
Supervisor Agent (Phase 10) ──► investigates using tools, never inventing facts
    │
    ▼
Decision Agent ──► recommendation only
    │
    ▼
Policy Engine ──► APPROVE | MANUAL_REVIEW | BLOCK
```

## Rule catalog (Phase 3)

| Rule | Signal |
|------|--------|
| `HIGH_TRANSACTION_AMOUNT` | Amount exceeds multiplier × customer average or absolute threshold |
| `NEW_DEVICE` | Unknown device or recently first associated |
| `NEW_LOCATION` | Country not in customer transaction history |
| `TRANSACTION_VELOCITY` | Too many transactions in a short window |
| `MULTIPLE_FAILED_LOGINS` | Failed login count exceeds threshold |
| `UNUSUAL_MERCHANT_CATEGORY` | New MCC category or high-risk merchant |
| `GEOGRAPHIC_ANOMALY` | Distance from home or impossible travel |

## Configuration

Thresholds and weights are externalized in `fraud-service/src/main/resources/application.yml` under `fraud.rules`.

## API

```http
POST /api/v1/fraud/evaluate/{transactionId}?persist=true
GET  /api/v1/fraud/alerts/{alertId}
```

Response fields: `alert_id`, `transaction_id`, `fraud_score`, `triggered_rules`, `severity`, `evidence`.
