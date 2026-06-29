
from __future__ import annotations

from typing import Any, Dict

from app.evaluator import evaluate_scenario
from app.models import PlannerRecommendation, Scenario


def validate_constraints(scenario: Scenario, recommendation: PlannerRecommendation) -> Dict[str, Any]:
    result = evaluate_scenario(scenario, recommendation)
    safety_review = result.safety_review.model_dump() if result.safety_review else None
    return {
        "scenario_id": result.scenario_id,
        "is_valid": result.status != "safety_failure",
        "status": result.status,
        "resilience_met": result.resilience_met,
        "estimated_endurance_hours": result.estimated_endurance_hours,
        "summary": result.summary,
        "safety_review": safety_review,
    }


def simulate_dispatch(scenario: Scenario, recommendation: PlannerRecommendation) -> Dict[str, Any]:
    result = evaluate_scenario(scenario, recommendation)
    routed_power_kw = (
        recommendation.solar_draw_kw
        + recommendation.grid_draw_kw
        + recommendation.battery_draw_kw
        + recommendation.generator_draw_kw
    )
    demand = scenario.demand
    total_demand_kw = demand.critical_load_kw + demand.vessel_load_kw + demand.other_load_kw
    unmet_load_kw = max(0.0, total_demand_kw - routed_power_kw)

    return {
        "scenario_id": result.scenario_id,
        "status": result.status,
        "resilience_met": result.resilience_met,
        "renewable_fraction": result.renewable_fraction,
        "estimated_endurance_hours": result.estimated_endurance_hours,
        "summary": result.summary,
        "served_load_kw": routed_power_kw,
        "total_demand_kw": total_demand_kw,
        "unmet_load_kw": unmet_load_kw,
        "grid_import_kw": recommendation.grid_draw_kw + recommendation.grid_to_battery_kw,
        "grid_export_kw": recommendation.grid_export_kw,
        "battery_discharge_kw": recommendation.battery_draw_kw,
        "battery_charge_kw": recommendation.battery_charge_kw + recommendation.grid_to_battery_kw,
        "generator_output_kw": recommendation.generator_draw_kw,
        "solar_to_port_kw": recommendation.solar_draw_kw,
        "solar_to_battery_kw": recommendation.battery_charge_kw,
        "warnings": recommendation.warnings,
        "safety_review": result.safety_review.model_dump() if result.safety_review else None,
    }