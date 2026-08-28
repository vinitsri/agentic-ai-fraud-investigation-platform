# Data Flow

## Interactive animation

The README embeds a looping GIF (`assets/data-flow-animation.gif`) showing the **full platform flow** — from payment event through fraud detection, AI investigation, and final decision (approve, block, or manual review). Regenerate it with:

```bash
python3 scripts/generate-data-flow-gif.py
```

For Play/Pause controls and three full flows, open [`interactive-data-flow.html`](interactive-data-flow.html) in a browser:

```bash
open docs/architecture/interactive-data-flow.html
```

## Phase 2 (Current)

```
Synthetic Generator → CSV → PostgreSQL
```

## Target Flow (Full Platform)

```
Transaction → Kafka → Fraud Service → Alert → Supervisor Agent
    → Specialist Agents + Tools → Decision Agent → Policy Engine → Analyst
```

See [data-model.md](data-model.md) for schema details.
