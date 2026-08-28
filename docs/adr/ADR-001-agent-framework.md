# ADR-001: Agent Framework Selection

## Status
Proposed

## Context
The platform requires multi-agent orchestration with conditional routing, tool calling, state management, and human-in-the-loop support.

## Options Considered
1. **LangGraph** — graph-based orchestration, strong state management
2. **CrewAI** — role-based agents, less flexible routing
3. **Custom orchestrator** — full control, high maintenance

## Decision
Use **LangGraph** for agent orchestration (Phase 10).

## Trade-offs
- (+) Explicit graph control, conditional edges, checkpointing
- (-) Steeper learning curve than simple chains

## Consequences
- Agents implemented as LangGraph nodes with shared investigation state
- Supervisor implements dynamic routing via conditional edges
