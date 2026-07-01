# Port Energy Multi-Agent Operations Assistant

A multi-agent decision-support system for business continuity during port energy disruption scenarios.

This project combines a FastAPI application with an agent orchestration layer to assess disruptions, generate routing plans, enforce safety guardrails, and evaluate operational recommendations. It is designed as an independent Agents for Business project.

## Problem

Ports rely on stable energy availability to maintain critical operations, vessel support, and safe routing decisions. During disruptions, operators need fast, structured guidance on how to allocate available energy sources while maintaining resilience and avoiding unsafe operating conditions.

Traditional dashboards can display data, but they do not coordinate reasoning across planning, safety review, and decision evaluation. This project explores how an agent-based system can support that workflow. 

## Solution

The system accepts predefined or custom disruption scenarios and produces an operator-facing recommendation that includes:
- operational status,
- routing recommendation,
- rationale,
- safety review,
- warnings,
- escalation conditions,
- estimated endurance.

The application keeps deterministic operational logic while adding an agent layer that separates planning, safety oversight, and evaluation responsibilities.

## Agent Architecture

The project uses a multi-agent architecture with four roles:

- **Coordinator Agent**: Orchestrates the workflow and combines outputs.
- **Operations Planner Agent**: Proposes an energy-routing plan using resilience-first logic.
- **Safety Reviewer Agent**: Validates the plan against operational and safety constraints.
- **Evaluation Agent**: Assesses decision quality, consistency, and scenario outcomes.

## Tools

The agents use structured tools from the application layer:
- scenario tools,
- simulation tools,
- policy tools,
- guardrail and escalation logic,
- evaluation cases.

## Course Concepts Demonstrated

This capstone demonstrates multiple concepts from the 5-Day AI Agents course:

1. **Multi-agent orchestration** through specialized agents with distinct responsibilities.
2. **Tool use and interoperability** by connecting agents to scenario, policy, and simulation tools.
3. **Guardrails and safety oversight** through policy enforcement and supervisor escalation.
4. **Evaluation workflows** using scenario-based evaluation cases and testable outputs.

## Features

- Predefined and custom disruption scenarios.
- Resilience-first energy-routing logic.
- Safety and feasibility validation.
- Operator-facing rationale and warnings.
- Supervisor escalation when endurance drops below threshold.
- Evaluation-ready scenario cases.
- FastAPI web interface and API endpoints.

## Project Structure

```text
app/
  agents.py
  evaluator.py
  main.py
  models.py
  policies.py
  adk/
  tools/
data/
evals/
guardrails/
templates/
static/
tests/
```

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

Open the app:

```text
http://127.0.0.1:8000
```

## Run Tests

```bash
uv run pytest
```

## Run Evaluation Cases

```bash
uv run pytest
```

You can also inspect the scenario evaluation inputs in:

```text
evals/eval_cases.yaml
```

## Demo Scenarios

- Grid disruption with critical-load prioritization.
- Custom scenario with limited battery and import constraints.
- Safety-failure scenario where the proposed plan is rejected.
- Low-endurance scenario requiring supervisor escalation.

## Why this project matters

This project shows how agents can support business operations with structured reasoning, safety checks, and auditable recommendations instead of open-ended chat alone.

## Capstone Links

- **GitHub Repository:** add your repository URL here
- **Demo Video:** add your YouTube link here
- **Kaggle Capstone Writeup:** add your Kaggle submission link here