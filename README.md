# Port Energy Multi-Agent Operations Assistant

A multi-agent decision-support system for business continuity during port energy disruption scenarios.

This project combines a FastAPI application with a multi-agent orchestration layer that assesses disruptions, proposes routing plans, applies safety guardrails, and evaluates operational recommendations. It is presented as an independent **Agents for Business** capstone project.

## Problem

Port operations depend on stable energy availability to support critical services, vessel demand, and safe operational continuity. During disruptions, operators must decide how to allocate limited energy resources while protecting resilience, maintaining safety, and responding quickly.

Traditional dashboards are useful for monitoring, but they do not coordinate planning, safety review, and decision evaluation in one workflow. This project explores how a multi-agent system can support that process with structured and auditable recommendations.

## Solution

The system accepts predefined and custom disruption scenarios and produces an operator-facing recommendation that includes:

- Operational status
- Energy-routing recommendation
- Decision rationale
- Safety review
- Warnings and violations
- Supervisor escalation conditions
- Estimated endurance

The core operational logic remains deterministic, while the agent layer makes the reasoning workflow explicit by separating planning, safety oversight, and evaluation responsibilities.

## Track

**Agents for Business**

## Agent Architecture

This project uses a multi-agent architecture with four roles:

- **Coordinator Agent**: Orchestrates the workflow and combines outputs from specialized agents.
- **Operations Planner Agent**: Proposes an energy-routing plan using resilience-first logic.
- **Safety Reviewer Agent**: Validates the proposed plan against operating constraints and escalation rules.
- **Evaluation Agent**: Assesses decision quality, scenario outcome, and evaluation readiness.

### Workflow

```text
User Input
   ↓
PortEnergyCoordinatorAgent
   ├── OperationsPlannerAgent
   ├── SafetyReviewerAgent
   └── EvaluationAgent
   ↓
Deterministic policy validation
   ↓
Final recommendation + safety review + agent trace
```

This design follows the core multi-agent pattern of using specialized agents instead of a single overloaded agent, with a coordinator responsible for routing, orchestration, and final aggregation. [Google ADK guidance]

## Tools

The agent layer uses structured tools from the application logic, including:

- Scenario retrieval tools
- Simulation and routing tools
- Policy and constraint-checking tools
- Guardrail and escalation logic
- Evaluation cases and test workflows

## Course Concepts Demonstrated

This capstone demonstrates at least four concepts from the 5-Day AI Agents course:

1. **Multi-agent orchestration** through specialized agents with distinct responsibilities
2. **Tool use and interoperability** by connecting agents to scenario, policy, and routing logic
3. **Guardrails and safety oversight** through safety validation and supervisor escalation
4. **Evaluation workflows** using scenario-based evaluation cases and testable outputs

## Features

- Predefined disruption scenarios
- Custom scenario input
- Resilience-first energy-routing logic
- Safety and feasibility validation
- Operator-facing rationale and warnings
- Supervisor escalation when endurance falls below threshold
- Agent trace visibility for capstone demonstration
- FastAPI web interface and API endpoints
- Test suite for smoke, policy, and UI checks

## API Endpoints

### Core workflow
- `GET /api/scenarios`
- `GET /api/scenarios/{scenario_id}`
- `POST /api/evaluate/{scenario_id}`
- `POST /api/evaluate-custom`

### Multi-agent capstone workflow
- `POST /api/agents/evaluate/{scenario_id}`
- `POST /api/agents/evaluate-custom`

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

Run the application:

```bash
uv run uvicorn app.main:app --reload
```

Open in the browser:

```text
http://127.0.0.1:8000
```

## Run Tests

```bash
uv run pytest tests
```

## Run Demo API Calls

Predefined scenario:

```bash
curl -X POST http://127.0.0.1:8000/api/agents/evaluate/normal_ops_01 | python3 -m json.tool
```

Custom scenario:

```bash
curl -X POST http://127.0.0.1:8000/api/agents/evaluate-custom \
  -H "Content-Type: application/json" \
  -d '{
    "critical_load_kw": 20,
    "vessel_load_kw": 15,
    "other_load_kw": 5,
    "solar_kw": 10,
    "battery_charge_kwh": 40,
    "battery_max_kwh": 100,
    "grid_available": true,
    "max_grid_import_kw": 25,
    "backup_generator_capacity_kw": 20,
    "backup_running_percentage": 0,
    "description": "Capstone test scenario"
  }' | python3 -m json.tool
```

## Evaluation Cases

Scenario evaluation inputs are available in:

```text
evals/eval_cases.yaml
```

The current repository also includes automated tests for smoke coverage, policy behavior, and UI-facing content.

## Demo Scenarios

- Grid disruption with critical-load prioritization
- Custom scenario with limited battery and grid import constraints
- Safety-failure scenario where the proposed plan is rejected
- Low-endurance scenario requiring supervisor escalation

## Why this project matters

This project shows how multi-agent systems can support business operations with structured reasoning, safety checks, traceable workflows, and auditable recommendations instead of open-ended chat alone.

It is intended as a practical example of how agent-based systems can be applied to operational continuity and disruption-response decision support.

## Capstone Links

- **GitHub Repository:** [https://github.com/haadihaa/port-energy-dt-ops-assistant](https://github.com/haadihaa/port-energy-dt-ops-assistant)
- **Demo Video:** add your YouTube link here
- **Kaggle Capstone Writeup:** add your Kaggle submission link here