# Agent Architecture

Multi-agent investigation orchestrated by a Supervisor Agent using LangGraph (Phase 10).

## Agents

| Agent | Responsibility |
|-------|----------------|
| Supervisor | Route investigation, coordinate agents |
| Transaction | Amount, velocity, merchant patterns |
| Customer | Profile, account age, spending behavior |
| Device | Device history, IP, location |
| Fraud RAG | Similar historical cases via pgvector |
| Decision | Consolidate evidence, recommend action |

## Investigation Flow

The Supervisor dynamically selects which agents to invoke based on alert context — not a fixed pipeline.

Decision Agent output feeds the **Policy Engine**, not direct execution.

Implementation begins in Phase 6.
