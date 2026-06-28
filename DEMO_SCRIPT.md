# Demo Script

## Goal
Show a complete end-to-end operator workflow in under 3 minutes.

## Opening
Hi, this is my capstone project: Port Energy Digital Twin Ops Assistant.

It is a local-first, multi-agent decision-support prototype for small-port energy operations under disruption scenarios. The system prioritizes resilience first, then emissions, then cost.

## Show the homepage
Open the app in the browser.

Say:
This is the operator console. It lets me choose a predefined disruption scenario, inspect the simulated context, and run an evaluation.

## Show scenario selection
Select a scenario.

Say:
Here I can load a scenario and review the current operational context, including critical load, vessel demand, solar availability, battery level, and grid status.

## Show the loading state
Pause briefly while the scenario loads.

Say:
The interface includes lightweight status feedback so the operator can see when scenario data or evaluation results are being loaded.

## Run evaluation
Click the evaluation button.

Say:
Now I run the operator evaluation. The planner agent proposes an energy-routing recommendation, and the reviewer agent checks it for safety and constraints before the result is shown.

## Show result section
Scroll through the result.

Say:
Here we can see the overall evaluation status, the proposed power-routing allocations, the planner rationale, and the safety review output.

## Show warnings and violations
Point to the safety section.

Say:
The result area explicitly shows warnings and violations, and if there are none, the UI says so clearly. This makes the output easier to review during a demo or operational walkthrough.

## Explain course concepts
Say:
This project demonstrates several course concepts:
- a multi-agent planner/reviewer pattern,
- agent skills through a dedicated assessment skill,
- structured outputs and validation,
- and safety-aware agent behavior in a local-first workflow.

## Closing
Say:
This is not a production control system. It is a local-first capstone prototype that shows how agent design can support resilient infrastructure decision-making in a clear and reviewable way.