---
name: port-ops-assessment
description: Assess simulated small-port energy scenarios and generate structured operational energy routing policies.
---

# Skill: Port Ops Assessment

## 1. Goal
Evaluate a simulated small-port energy scenario config and generate structured routing recommendations that prioritize infrastructure resilience, minimize emissions, and optimize utility costs.

## 2. Expected Inputs
Structured scenario config containing:
- **Grid Status:** Current state of utility connection (e.g., online, offline).
- **Vessel Demand:** Predicted vessel shore power load (in kW).
- **Renewable Generation:** Available solar generation forecast (in kW).
- **Battery State:** Current battery capacity (kWh), maximum capacity (kWh), and charge/discharge constraints (kW).
- **Critical Load:** Minimum power required (in kW) to sustain basic port operations.

## 3. Expected Outputs
A structured plan compatible with Pydantic validation:
- **Routing Decision:** Specific allocation mapping (Grid to Port, Solar to Battery/Port, Battery to Port, Generator to Port).
- **Resilience Status:** Boolean flag indicating if the critical load is successfully met.
- **Safety Status:** Verification that all battery and line limits are respected.
- **Priority Alignment:** Explicit statement of how the decision aligns with the resilience-first priority.

## 4. Assessment Rules
- **Rule 1 (Resilience):** Critical load must be served first. If renewable and battery sources are insufficient during a grid outage, flag the shortfall immediately.
- **Rule 2 (Emissions):** Allocate solar power directly to the port load and battery charging before drawing from utility grid or auxiliary sources.
- **Rule 3 (Cost):** Draw from the grid only when available and only if renewable/battery sources cannot cover non-critical loads, avoiding peak charge thresholds if battery reserves permit.

## 5. Escalation Rules
- **Insufficient Energy:** If the scenario parameters mathematically show that critical load cannot be met, raise an immediate alert state rather than generating a false success path.
- **Ambiguous Inputs:** If any physical capacity parameters (e.g., maximum charge rate) are missing or mathematically invalid, escalate immediately to the user.

## 6. Important Constraints
- Operate strictly on static scenario data. Do not make telemetry, sensor integration, or external API lookup calls.
- Recommendations must be concise, specific, and action-oriented. Avoid verbose descriptions.
