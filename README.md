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
- Battery input shown as a percentage.
- Direction-aware routing display with import, charging, discharge, and export flows.

## Workflow

The system uses two roles:

- **Operations Planner Agent** proposes an energy-routing plan.
- **Safety Reviewer Agent** validates that exact plan against physical and operational constraints.

The evaluation can return results such as:

- `success`
- `unmet_critical_load`
- `safety_failure`
- `insufficient_information`

## Routing Logic

The planner follows a resilience-first routing policy:

1. Use renewable energy directly first.
2. If demand remains, use grid import next when available.
3. Then use battery discharge.
4. Use backup generation last.

When there is surplus energy:

1. Keep backup generation off.
2. Charge the battery toward the 80% operating target when possible.
3. Export any remaining surplus to the grid when the grid is available.

## What the App Shows

For each scenario, the interface presents:

- status,
- supervisor alert when required,
- proposed energy routing,
- planner rationale,
- safety and constraints review,
- operational notes,
- estimated endurance.

The routing display is direction-aware and can show flows such as:

- Solar → Port
- Solar → Battery
- Grid → Port
- Grid → Battery
- Port → Grid
- Battery → Port
- Generator → Port

## Custom Scenario Inputs

The custom scenario form allows operators to define:

- critical load,
- vessel demand,
- other load,
- solar capacity,
- battery capacity,
- battery level as a percentage,
- grid availability,
- maximum grid import,
- backup generator capacity,
- optional scenario notes.

Battery level is entered in percentage terms in the UI, while the backend converts it into stored energy using the configured battery capacity. The default operating target is 80% of battery capacity.

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

## Project Structure

A simplified project structure:

```text
app/
  evaluator.py
  main.py
  models.py
  policies.py
static/
  style.css
templates/
  index.html
tests/
  ...
```

## Notes

This is a practical MVP focused on structured agent behavior and explainable operational decision support. The current version uses simplified assumptions for endurance, battery charging, and backup generation behavior, so it should be understood as a prototype rather than a production control system.

## Author

Designed and developed by Mohammad Hadi Hamednia.