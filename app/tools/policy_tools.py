from __future__ import annotations

from typing import Any, Dict

from app.models import PlannerRecommendation, Scenario
from app.policies import compute_routing_policy


POLICY_SUMMARY = {
    "routing_priority": [
        "renewables_first",
        "grid_before_battery_when_available",
        "battery_before_backup_generator",
        "backup_generator_last",
    ],
    "surplus_priority": [
        "serve_demand_first",
        "turn_off_unneeded_generator",
        "charge_battery_toward_80_percent",
        "export_remaining_surplus_when_grid_available",
    ],
    "guardrails": [
        "grid_use_must_respect_max_grid_import",
        "battery_charge_and_discharge_must_respect_capacity",
        "generator_output_must_not_exceed_available_capacity",
        "deterministic_validation_remains_authoritative",
    ],
}


def explain_policy() -> Dict[str, Any]:
    return POLICY_SUMMARY


def propose_deterministic_plan(scenario: Scenario) -> PlannerRecommendation:
    return compute_routing_policy(scenario)


def recommendation_to_dict(recommendation: PlannerRecommendation) -> Dict[str, Any]:
    return recommendation.model_dump()