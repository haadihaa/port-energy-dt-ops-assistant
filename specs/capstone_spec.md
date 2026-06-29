# Naviclean Capstone Specification

## Project title
Naviclean: Hybrid Multi-Agent Port Energy Resilience Assistant

## Problem statement
Ports operating under disruption scenarios need fast, explainable energy-routing decisions that preserve critical loads, minimize unmet demand, and respect hard operating constraints. The current project already contains deterministic routing and safety logic, but it should be upgraded into a capstone-ready agentic system that demonstrates advanced reasoning, external tool use, independent review, and guardrails.

## Capstone goal
Turn the existing prototype into a hybrid multi-agent decision-support system in which:
- an LLM Planner Agent proposes an energy dispatch plan,
- external tools compute simulation and validation results,
- an independent Reviewer Agent approves, rejects, or escalates the plan,
- hard safety constraints remain deterministic,
- high-risk actions require a human-in-the-loop checkpoint.

This project is not a free-form chatbot. It is an agentic operational system for disruption-aware port energy planning.

## Why this architecture
The capstone should demonstrate real agent behavior rather than only text generation. The system must show:
- reasoning over structured scenarios,
- external tool use,
- multi-agent coordination,
- constraint-aware planning,
- behavioral evaluation,
- policy gating and human approval.

The existing routing engine is retained as the truth layer because domain safety rules should not depend on probabilistic prompting.

## Existing domain rules to preserve
The upgraded architecture must preserve the current routing and safety behavior already defined in the project:
- Use available renewable energy directly first.
- When there is a deficit, use grid import first when available, then battery, then backup generator.
- When there is a surplus, charge the battery toward 80% first, then turn off backup generation, then export to the grid.
- Support a configurable maximum grid import in grid-on mode.
- Treat `backup_generator_capacity_kw` as rated capacity.
- Treat `backup_running_percentage` as the operating percentage of rated generator capacity.
- Reject generator operation below 30% of rated capacity.
- Keep the generator available even when backup is initially off, because it may still be needed under deficit conditions.

## Target users
- Port operations planners
- Energy resilience analysts
- Digital-twin demo audiences
- Capstone evaluators looking for an agentic workflow with safety controls

## Core user story
A user selects or configures a disruption scenario. The Planner Agent studies the scenario, calls tools to simulate feasible dispatch options, proposes a structured plan, and explains why the plan best satisfies resilience goals. A separate Reviewer Agent independently validates the same plan and either approves it, requests revision, or escalates it for manual review.

## System scope
The system will recommend and justify energy-routing actions. It will not autonomously execute real-world controls. Any future execution step must be behind an explicit policy gate and human approval.

## Agent roles

### 1. Planner Agent
Responsibilities:
- Read scenario state and disruption context.
- Generate one or more candidate dispatch plans.
- Call tools to test feasibility and quality.
- Select the best valid plan.
- Return strict JSON with plan, rationale, assumptions, and confidence.

Required output schema:
```json
{
  "plan_id": "string",
  "scenario_id": "string",
  "actions": [
    {
      "source": "renewables|grid|battery|generator",
      "power_kw": 0,
      "status": "on|off|charge|discharge|idle"
    }
  ],
  "expected_outcomes": {
    "critical_load_served_kw": 0,
    "vessel_load_served_kw": 0,
    "unmet_load_kw": 0,
    "battery_soc_end_pct": 0,
    "generator_output_kw": 0,
    "grid_import_kw": 0,
    "estimated_endurance_hours": 0,
    "renewable_share_pct": 0
  },
  "assumptions": ["string"],
  "rationale": "string",
  "confidence": 0.0
}
```

### 2. Reviewer Agent
Responsibilities:
- Receive the exact planner output.
- Re-run validation and simulation tools.
- Check policy compliance and rule adherence.
- Return `approve`, `revise`, or `escalate`.
- Provide concise rejection feedback when revision is required.

Required output schema:
```json
{
  "decision": "approve|revise|escalate",
  "issues": ["string"],
  "policy_flags": ["string"],
  "review_summary": "string"
}
```

## Tool layer
The agent layer must call deterministic tools rather than invent results in free text.

### Required tools
1. `get_scenario_state(scenario_id)`
   - Returns structured state for loads, renewable availability, battery, generator, grid status, and disruption parameters.

2. `simulate_dispatch(plan)`
   - Computes load served, unmet load, renewable share, battery state transition, generator output, grid import, and endurance.

3. `validate_constraints(plan)`
   - Checks generator minimum load, battery operating limits, grid import cap, invalid negative values, and impossible dispatch combinations.

4. `explain_policy()`
   - Returns the operational policy rules used by the system.

### Optional tools
- `score_resilience(plan)`
- `compare_candidate_plans(candidates)`
- `load_predefined_scenario(name)`
- `generate_operator_report(plan)`

## Decision flow
1. User selects a predefined or custom disruption scenario.
2. Planner Agent retrieves scenario state.
3. Planner Agent proposes an initial dispatch plan.
4. Planner Agent calls simulation and validation tools.
5. If invalid, Planner Agent revises the plan.
6. Reviewer Agent independently checks the final planner proposal.
7. Reviewer Agent returns approve, revise, or escalate.
8. If approved, the system displays the recommended plan and explanation.
9. If escalated, a human operator must review before any downstream action.

## Guardrails
The project must clearly demonstrate production-style safeguards.

### Policy gating
Use a `policy.yaml` file for deterministic restrictions such as:
- allowed tools by environment,
- blocked execution actions,
- no direct real-world actuation,
- reviewer approval required before reporting a plan as recommended.

### Human-in-the-loop
Any high-risk or future execution-like action must require explicit human confirmation. In the capstone demo, human approval can be modeled as a required confirmation step after reviewer approval.

### Sandboxing
Agent actions must be limited to local simulation and analysis. No external actuation or unsupervised side effects should be possible.

## Evaluation strategy
The capstone must include both deterministic tests and behavioral evaluation.

### Deterministic tests
Use unit tests to verify:
- routing priority order,
- generator minimum 30% enforcement,
- battery charge-to-80 behavior,
- grid import cap behavior,
- expected deficit and surplus handling.

### Behavioral evals
Add scenario-based evaluations that judge whether the agent:
- uses tools before finalizing a plan,
- avoids violating hard constraints,
- gives a reviewer-consistent recommendation,
- chooses a sensible plan under disruption,
- escalates when conditions are ambiguous or unsafe.

### Minimum eval set
Create at least 10 to 20 scenarios across:
- normal operation,
- grid-online disruption,
- grid-offline operation,
- low battery conditions,
- undersized generator conditions,
- renewable surplus,
- conflicting or unsafe input states.

## BDD scenario categories
The repository should include a Gherkin file covering at minimum:
- renewable-first dispatch,
- grid-first deficit handling,
- battery charge priority during surplus,
- generator rejection below 30%,
- reviewer rejection of an unsafe plan,
- escalation when no valid plan exists,
- comparison of multiple candidate plans,
- support for predefined and custom disruption scenarios.

## Repository structure
```text
port-energy-dt-ops-assistant/
├── README.md
├── specs/
│   ├── capstone_spec.md
│   └── scenarios.feature
├── agents/
│   ├── planner_agent.py
│   └── reviewer_agent.py
├── tools/
│   ├── scenario_tools.py
│   ├── simulation_tools.py
│   └── policy_tools.py
├── guardrails/
│   ├── policy.yaml
│   └── hitl.py
├── evals/
│   ├── eval_cases.yaml
│   └── judge.py
├── tests/
└── app/
```

## Implementation plan

### Phase 1: formalize the project
- Add `specs/capstone_spec.md`.
- Add `specs/scenarios.feature`.
- Document the current deterministic routing rules in README language suitable for Kaggle.

### Phase 2: convert logic into tools
- Wrap existing routing and evaluator code as reusable tool functions.
- Standardize JSON input and output contracts.
- Ensure all tool outputs are auditable and deterministic.

### Phase 3: add agent orchestration
- Implement Planner Agent with strict JSON output.
- Implement Reviewer Agent with independent validation.
- Add a one-retry revision loop.

### Phase 4: add guardrails and evaluation
- Add `policy.yaml` and human confirmation checkpoint.
- Build scenario-based evaluation cases.
- Record benchmark outputs for the README and demo.

## Demo expectations
The capstone demo should show:
- a user selecting a disruption scenario,
- the planner calling tools,
- the reviewer independently checking the plan,
- a rejected plan being revised or escalated,
- a final approved recommendation with explanation,
- visible evidence that hard safety logic remained deterministic.

## Capstone success criteria
The project succeeds if it demonstrates all of the following:
1. Multi-agent workflow, not a single prompt.
2. External tool use during planning and review.
3. Deterministic safety constraints outside the model.
4. Human approval or escalation path for risky outcomes.
5. Scenario-based evaluation in addition to unit tests.
6. Clear alignment with the existing energy-routing logic.
7. Kaggle-friendly documentation and demo narrative.

## Suggested README positioning
Use language like this in the README:

> Naviclean is a hybrid multi-agent port energy resilience assistant. An LLM Planner Agent proposes dispatch plans for disruption scenarios, deterministic tools simulate and validate those plans, and an independent Reviewer Agent checks safety before approval. The system combines advanced reasoning with hard operational guardrails.

## Out of scope
- Real hardware control
- Autonomous deployment to real energy infrastructure
- Pure LLM decision-making without deterministic checks
- Hidden tool calls or opaque recommendations without traceability

## Final note
The strongest capstone version of this project is not a rewrite. It is an upgrade of the existing deterministic prototype into a hybrid agent architecture that uses external tools, independent review, and explicit guardrails.