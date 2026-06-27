# Repository Context: Port Energy Digital Twin Ops Assistant

## 1. Project Purpose
This repository is a local-first, scenario-based decision-support prototype designed to assist operators in small-port energy management. Inspired by digital twin concepts, it models energy assets (solar, batteries, vessel shore power) and evaluates operational routing policies under simulated disruption scenarios.

## 2. Core Decision Priority Hierarchy
All agent recommendations, optimization functions, and heuristic policies must strictly enforce the following hierarchy:
1. **Resilience & Reliability:** Keep critical port infrastructure operational under all circumstances.
2. **Emissions Reduction:** Maximize local renewable utilization and storage before using fossil-fuel auxiliary generation.
3. **Operational Cost Optimization:** Minimize peak grid charges and general utility expenditures when safety and environmental priorities allow.

## 3. Scope Constraints
- **Scenario-Based Only:** No live connections, no real-time telemetry, and no SCADA/hardware integration. Data consists entirely of static or simulated JSON scenarios.
- **Local-First:** Designed to run entirely on the developer's localhost. Do not propose Docker, cloud deployments (AWS, GCP), or external database setups.
- **Two-Agent Architecture:** Maintain a strict separation of concerns between exactly two agents:
  1. **Operations Planner Agent:** Proposes routing choices and policy adjustments.
  2. **Safety Reviewer Agent:** Independently evaluates proposed plans against physical safety envelopes and constraints.

## 4. Implementation Principles
- **Structured Contracts:** All interfaces between backend logic, frontend templates, and agents must use explicit Pydantic schemas for input and output validation.
- **Incremental Steps:** Implement and modify code in small, testable chunks. Verify each change before proceeding.
- **Simplicity Over Novelty:** Choose standard, readable Python patterns. Do not introduce complex frameworks, message brokers, or asynchronous engines unless requested.

## 5. Safety and Guardrail Principles
- The Safety Reviewer Agent must evaluate recommendations mathematically (e.g., verifying that battery charge state is within 0% to 100%, and total energy supply matches load requirements).
- The system must never suggest actions that violate physical limits, even if they would optimize emissions or costs.

## 6. Coding-Agent Behavior Rules
- **No Feature Creep:** Implement only the requested features. Do not add speculative "future work" utilities or modules.
- **Escalate Uncertainty:** If a requirement is ambiguous, or if simulated equations are conflicting, stop and ask the user for clarification instead of guessing or faking a solution.
- **Respect Scaffolding:** Adhere strictly to the defined project folder structure. Keep dependencies clean, matching `pyproject.toml`.
