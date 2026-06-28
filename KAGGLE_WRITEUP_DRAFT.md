# Port Energy Digital Twin Ops Assistant

## Track
Agents for Business

## Subtitle
A local-first multi-agent decision-support prototype for resilient small-port energy operations under disruption scenarios.

## Summary

Port Energy Digital Twin Ops Assistant is a local-first capstone prototype that helps small-port operators evaluate simulated disruption scenarios and review structured energy-routing recommendations. The system is designed around a resilience-first decision hierarchy: maintain critical port operations first, then improve clean energy utilization, then reduce unnecessary grid or generator cost exposure.

The project focuses on a practical operational problem: during outages or constrained supply conditions, a port operator must decide how to allocate available energy resources such as solar, battery storage, grid power, and auxiliary generation. Instead of relying on a single opaque agent response, this prototype uses a two-agent workflow in which a planner proposes a recommendation and a reviewer checks it for safety and feasibility before it is presented in the interface.

## Problem

Small ports face difficult trade-offs when balancing:
- critical facility loads,
- vessel shore-power demand,
- grid availability,
- battery constraints,
- and renewable energy utilization.

In disruption scenarios, operators need support that is fast, explainable, and lightweight. A full production optimization platform is out of scope for a capstone project, but a local-first decision-support tool can still demonstrate meaningful agent design and operational value.

## Solution

This project provides:
- a FastAPI backend,
- a local browser-based operator UI,
- predefined disruption scenarios,
- structured scenario evaluation,
- a planner/reviewer multi-agent pattern,
- explicit safety review output.

The user selects a scenario, loads its details, and runs an evaluation. The system returns:
- recommendation status,
- proposed power-routing allocations,
- planner rationale,
- alignment to decision priorities,
- safety pass/fail result,
- warnings and violations.

This makes the output easier to inspect than a free-form assistant response and better suited to operational review.

## Agent Architecture

### 1. Operations Planner Agent
The planner evaluates the scenario and proposes a routing strategy that prioritizes:
1. resilience and continuity of critical operations,
2. cleaner local energy usage,
3. cost awareness when feasible.

### 2. Safety Reviewer Agent
The reviewer checks the proposed recommendation against constraints and returns:
- whether the recommendation is safe,
- any violations,
- any warnings,
- operational review notes.

This separation creates a simple but strong multi-agent workflow: propose first, review second.

## Course Concepts Demonstrated

### Multi-agent systems
The project uses a planner/reviewer architecture instead of a single generic agent.

### Agent skills
The repository includes a dedicated `port-ops-assessment` skill definition for structured scenario assessment and routing-policy reasoning.

### Structured outputs
The project emphasizes structured evaluation results and review outputs suitable for backend logic and UI presentation.

### Safety features
The recommendation is explicitly checked before presentation to the operator.

### Local-first workflow
The prototype runs locally with a simple developer setup and browser interface.

## Technical Stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- Jinja2
- Vanilla HTML/CSS/JavaScript
- pytest

## Current MVP Features

- local UI served from `/`
- scenario selection and detail loading
- evaluation execution from the browser
- loading-state feedback
- structured result rendering
- planner rationale display
- safety review display
- explicit warning/violation sections
- automated tests including FastAPI smoke tests

## Why This Matters

This project shows how agent systems can support operational decision-making in infrastructure contexts without pretending to be a production autonomous control system. It is intentionally scoped as a local-first prototype that emphasizes transparency, reviewability, and practical capstone value.

## Repository

[Add your GitHub repo link here]

## Demo Video

[Add your demo video link here]