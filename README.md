# Port Energy Digital Twin Ops Assistant

A local-first, two-agent decision-support prototype designed to assist operators in small-port energy management. The system models simulated port assets (such as solar arrays, battery storage, and vessel shore power) and evaluates operational policies under hypothetical disruption scenarios. It uses a structured agent workflow to recommend actions that prioritize grid resilience, minimize emissions, and optimize operational costs.

## Problem Statement
Small-port operators face complex trade-offs when balancing grid reliability, environmental footprints, and utility budgets. During disruptions—such as utility grid outages or sudden spikes in vessel power demands—operators lack lightweight decision-support tools that can quickly ingest scenario parameters, evaluate alternative energy-routing policies, and recommend mitigation steps under multi-objective constraints.

## What the System Does
- Models simulated operational scenarios and grid disruptions for a simplified port energy network.
- Evaluates rule-based and LLM-assisted energy routing policies under hypothetical scenarios.
- Coordinates a two-agent workflow to analyze scenario impacts, propose mitigation strategies, and review recommendations.
- Renders a simple local dashboard for operators to run scenarios, compare policy outputs, and review agent recommendations.

## What the System Does Not Do
- **No real-time telemetry:** The system operates on static/simulated scenario configurations and does not connect to live physical sensors or SCADA systems.
- **No production deployment:** It is designed to run locally for development, educational demonstrations, and prototyping.
- **No autonomous control:** The agents suggest operational recommendations but do not execute physical switching or energy-routing actions.

## Core Priorities (Hierarchy of Decisions)
1. **Resilience & Reliability:** Keep critical port infrastructure powered at all times (e.g., maintaining communication, minimal lighting, and emergency systems).
2. **Emissions Reduction:** Maximize the utilization of local renewable sources (solar) and battery storage before drawing from fossil-based utility or auxiliary generation.
3. **Operational Cost Optimization:** Minimize peak-demand charges and overall electricity costs when grid power is available.

## Agent Architecture Overview
The system relies on a two-agent collaboration workflow:
- **Operations Planner Agent:** Analyzes the simulated port state and current scenario constraints, and proposes energy-routing policy adjustments based on the priority hierarchy.
- **Safety Reviewer Agent:** Validates proposed policy recommendations against physical constraints (e.g., maximum battery charge/discharge rates, physical capacity limits) to ensure safety and operational feasibility.

## Course Concepts Demonstrated
- **Two-Agent Collaboration:** Structured delegation and verification between a planning agent and a checking/reviewing agent.
- **Structured LLM Outputs:** Use of Pydantic models for reliable schema validation of agent outputs.
- **Local-First Agent Patterns:** Designing workflows that perform effectively with lightweight, locally run model interfaces.

## Planned Stack
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic
- **UI:** Jinja2 templates, HTML5, Vanilla CSS
- **Testing:** pytest

## Planned Evaluation Approach
- **Policy Verification:** Unit testing mathematical constraints (e.g., charge state limits, power conservation rules).
- **Scenario Replay:** Replaying historical or synthetic scenario logs to verify that agent recommendations consistently prioritize resilience over emissions, and emissions over cost.

## Current Status
- **Phase:** Repository structure scaffolded. Initial dependencies and documentation configured. No runtime application logic has been implemented yet.
