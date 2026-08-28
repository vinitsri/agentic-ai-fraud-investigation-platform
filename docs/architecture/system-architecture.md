# System Architecture

Production-inspired architecture for autonomous fraud investigation with human oversight.

## Overview

```mermaid
flowchart TD
    T[Transaction] --> K[Kafka]
    K --> FDS[Fraud Detection Service]
    FDS --> RE[Rules Engine]
    FDS --> ML[ML Risk Model]
    FDS --> FA[Fraud Alert]
    FA --> SA[Supervisor Agent]
    SA --> TA[Transaction Agent]
    SA --> CA[Customer Agent]
    SA --> DA[Device Agent]
    SA --> RA[Fraud RAG Agent]
    TA --> DEC[Decision Agent]
    CA --> DEC
    DA --> DEC
    RA --> DEC
    DEC --> PE[Policy Engine]
    PE --> APPROVE[APPROVE]
    PE --> REVIEW[MANUAL_REVIEW]
    PE --> BLOCK[BLOCK]
    REVIEW --> HFA[Human Fraud Analyst]
```

## Components

| Component | Technology | Phase |
|-----------|------------|-------|
| Fraud Detection Service | Spring Boot | 3–4 |
| AI Investigation Service | FastAPI + LangGraph | 6–10 |
| Database | PostgreSQL + pgvector | 2, 9 |
| Event Streaming | Kafka | 11 |
| Analyst UI | React | 13 |

## Principles

1. LLM is not the source of truth — agents use tools for facts.
2. Business policies remain deterministic.
3. Human approval required for sensitive actions.
4. All agent actions are auditable.

See also: [data-model.md](data-model.md), [agent-architecture.md](agent-architecture.md).
