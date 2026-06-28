# Port Energy Digital Twin Ops Assistant

A local-first, two-agent decision-support prototype for small-port energy operations under disruption scenarios.

The project helps operators evaluate simulated energy-routing decisions during events such as grid outages, vessel shore-power demand spikes, and constrained on-site supply conditions. It prioritizes **resilience first**, then emissions reduction, then cost awareness. [cite:58]

## Overview

Small ports face operational trade-offs when balancing critical load continuity, vessel demand, distributed energy resources, and grid uncertainty. This prototype provides a lightweight operator-facing interface and a structured backend workflow for evaluating disruption scenarios and reviewing proposed energy-routing recommendations. [cite:246][cite:152]

The current MVP includes:
- a FastAPI backend,
- a local browser UI served from `/`,
- scenario selection and evaluation,
- a two-agent planning and review pattern,
- and automated tests including smoke tests for the real app request path. [cite:246][cite:327]

## Problem

During operational disruptions, small-port operators need decision support that is:
- fast to run locally,
- easy to inspect,
- resilient-first,
- and transparent enough for human review. [cite:58][cite:150]

Traditional optimization-heavy tools or production SCADA integrations are often out of scope for a small capstone prototype. This project instead focuses on a local-first simulation and agent-assisted evaluation workflow. [cite:150]

## Solution

The system models simplified port energy scenarios and runs an operator evaluation flow:
1. The user selects a predefined disruption scenario in the browser UI.
2. The backend evaluates the scenario and produces a structured recommendation.
3. A planner-style agent proposes an energy-routing approach.
4. A reviewer-style agent checks safety and feasibility constraints before the result is shown to the operator. [cite:152][cite:246]

## Agent Design

### Operations Planner Agent
The planner analyzes scenario conditions and proposes an energy-routing recommendation aligned to the project’s priority hierarchy:
1. maintain critical resilience,
2. use cleaner local energy where possible,
3. reduce unnecessary grid or generator dependence when feasible. [cite:58][cite:152]

### Safety Reviewer Agent
The reviewer checks whether the proposed recommendation respects operational and physical constraints, and returns:
- pass/fail safety status,
- violations,
- warnings,
- and feasibility feedback for operator review. [cite:152]

This creates a clear multi-agent pattern: proposal first, structured review second. [cite:152][cite:343]

## Current Features

- FastAPI application serving the root UI at `/`. [cite:246]
- Static assets mounted and rendered correctly. [cite:246]
- Scenario selection from backend-provided scenario data.
- Scenario detail display in the UI.
- Evaluation execution from the browser with visible loading-state feedback. [cite:296]
- Result display including:
  - status banner,
  - routing allocations,
  - planner rationale,
  - priority alignment,
  - safety review,
  - explicit warnings and violations sections. [cite:296]
- Clear empty-state messaging for warnings and violations when no items are present.
- Automated test coverage including direct policy tests and FastAPI `TestClient` smoke tests. [cite:327]

## Course Concepts Demonstrated

This project is designed to demonstrate multiple concepts from the course:

### 1. Multi-agent system design
The project uses a planner/reviewer pattern rather than a single undifferentiated agent response. [cite:152]

### 2. Agent skills
The repository includes a dedicated `port-ops-assessment` skill definition for assessing simulated port energy scenarios and structured routing policies. [cite:152]

### 3. Structured outputs and validation
The system uses structured backend logic and schema-oriented outputs suitable for reliable evaluation and UI rendering. The project design emphasizes explicit review rather than free-form agent behavior. [cite:150][cite:152]

### 4. Local-first agent workflow
The prototype is intentionally scoped to run locally with a simple web interface and lightweight developer workflow. [cite:246][cite:150]

### 5. Safety-aware agent behavior
Recommendations are reviewed before presentation, which makes the system more useful for operational decision support than a thin single-agent wrapper. [cite:152][cite:343]

## Stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- Jinja2 templates
- Vanilla HTML/CSS/JavaScript
- pytest [cite:327][cite:246]

## Project Structure

```text
port-energy-dt-ops-assistant/
├── app/
├── templates/
├── static/
├── tests/
├── .agents/
├── README.md
├── MILESTONE_1.md
└── pyproject.toml
```

## How to Run

### 1. Install dependencies
```bash
uv sync --extra dev
```

### 2. Start the app
```bash
uv run uvicorn app.main:app --reload
```

### 3. Open in browser
```text
http://127.0.0.1:8000/
```

## How to Run Tests

```bash
uv run pytest
```

The current test suite passes, including smoke tests for:
- `GET /`
- `GET /api/scenarios` [cite:327]

## Example Operator Flow

1. Open the local UI.
2. Select a disruption scenario such as a grid blackout.
3. Review scenario context and supply/demand values.
4. Run the operator evaluation.
5. Inspect:
   - recommendation status,
   - proposed routing values,
   - planner rationale,
   - safety review output,
   - warnings and violations. [cite:246][cite:296]

## What This Project Does Not Do

- It does not control real infrastructure.
- It does not ingest live SCADA or telemetry streams.
- It does not claim production-grade dispatch optimization.
- It does not execute autonomous switching actions. [cite:150]

This is a simulation-based, local-first capstone prototype for structured agent decision support.

## Current Status

Milestone 1 is complete:
- working local MVP,
- browser-based interaction flow,
- cleaner operator-facing UI,
- passing automated tests,
- project documentation and milestone tracking committed. [cite:327][cite:246]

## Next Steps

Planned Milestone 2 directions include:
- stronger scenario/result presentation,
- deeper safety and policy test coverage,
- submission packaging for the Kaggle capstone. [cite:85]