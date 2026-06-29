# Port Energy Digital Twin Ops Assistant

Port Energy Digital Twin Ops Assistant is a local-first, two-agent decision-support prototype for small-port energy operations under disruption scenarios. It helps operators evaluate how available energy sources should be routed to maintain critical operations while respecting operational constraints and prioritizing resilience first, then cleaner energy use, then cost.

## Features

- Two-agent evaluation workflow.
- Supports predefined and custom disruption scenarios.
- Resilience-first routing logic.
- Safety and feasibility validation of proposed routing plans.
- Estimated endurance display for the evaluated operating condition.
- Supervisor escalation when endurance falls below the critical threshold.
- Clear operator-facing outputs for routing, rationale, warnings, and required actions.

## Workflow

The system uses two roles:

- **Operations Planner Agent** proposes an energy-routing plan.
- **Safety Reviewer Agent** validates that exact plan against physical and operational constraints.

The evaluation can return results such as:

- `success`
- `unmet_critical_load`
- `safety_failure`
- `insufficient_information`

## What the App Shows

For each scenario, the interface presents:

- status,
- supervisor alert when required,
- proposed energy routing,
- planner rationale,
- safety and constraints review,
- operational notes,
- estimated endurance.

## Run Locally

Clone the repository:

```bash
git clone https://github.com/haadihaa/port-energy-dt-ops-assistant.git
cd port-energy-dt-ops-assistant
```

Install dependencies:

```bash
uv sync --extra dev
```

Run the app:

```bash
uv run uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Run Tests

```bash
uv run pytest
```

## Notes

This is a practical MVP focused on structured agent behavior and explainable operational decision support. The current version uses simplified assumptions for endurance and backup generation, so it should be understood as a prototype rather than a production control system.

## Author

Designed and developed by Mohammad Hadi Hamednia.