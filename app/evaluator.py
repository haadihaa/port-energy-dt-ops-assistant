from app.models import Scenario, EvaluationResult, SafetyReview, PlannerRecommendation


def evaluate_scenario(scenario: Scenario, recommendation: PlannerRecommendation) -> EvaluationResult:
    supply = scenario.supply
    demand = scenario.demand

    if (
        supply.solar_kw < 0
        or supply.battery_charge_kwh < 0
        or supply.battery_max_kwh <= 0
        or supply.max_grid_import_kw < 0
        or supply.backup_generator_kw < 0
        or demand.critical_load_kw < 0
        or demand.vessel_load_kw < 0
        or demand.other_load_kw < 0
    ):
        return EvaluationResult(
            scenario_id=scenario.scenario_id,
            status="insufficient_information",
            resilience_met=False,
            estimated_endurance_hours=None,
            summary="Invalid or negative capacity/demand values provided in scenario inputs."
        )

    violations = []
    warnings = []

    if (
        recommendation.grid_draw_kw < 0
        or recommendation.solar_draw_kw < 0
        or recommendation.battery_draw_kw < 0
        or recommendation.generator_draw_kw < 0
        or recommendation.battery_charge_kw < 0
        or recommendation.grid_to_battery_kw < 0
        or recommendation.grid_export_kw < 0
    ):
        violations.append("Recommendation contains negative energy routing values.")

    battery_level_percent = (supply.battery_charge_kwh / supply.battery_max_kwh) * 100.0
    if battery_level_percent > 100:
        violations.append(
            f"Battery level ({battery_level_percent:.1f}%) exceeds physical capacity."
        )

    if recommendation.grid_draw_kw > 0 and not supply.grid_available:
        violations.append("Grid draw requested but utility grid is offline.")

    if recommendation.grid_to_battery_kw > 0 and not supply.grid_available:
        violations.append("Grid-to-battery charging requested but utility grid is offline.")

    if recommendation.grid_export_kw > 0 and not supply.grid_available:
        violations.append("Grid export requested but utility grid is offline.")

    total_grid_use = recommendation.grid_draw_kw + recommendation.grid_to_battery_kw
    if total_grid_use > supply.max_grid_import_kw:
        violations.append(
            f"Total grid use ({total_grid_use:.1f} kW) exceeds maximum allowed grid import ({supply.max_grid_import_kw:.1f} kW)."
        )

    if recommendation.battery_draw_kw > supply.battery_charge_kwh:
        violations.append(
            f"Battery discharge draw ({recommendation.battery_draw_kw:.1f} kW) exceeds current stored charge ({supply.battery_charge_kwh:.1f} kWh)."
        )

    free_space = max(0.0, supply.battery_max_kwh - supply.battery_charge_kwh)
    total_battery_charge = recommendation.battery_charge_kw + recommendation.grid_to_battery_kw
    if total_battery_charge > free_space:
        violations.append(
            f"Battery charge allocation ({total_battery_charge:.1f} kW) exceeds free storage capacity ({free_space:.1f} kWh)."
        )

    total_solar_used = recommendation.solar_draw_kw + recommendation.battery_charge_kw
    if total_solar_used > supply.solar_kw:
        violations.append(
            f"Total solar allocation ({total_solar_used:.1f} kW) exceeds available solar generation ({supply.solar_kw:.1f} kW)."
        )

    if recommendation.generator_draw_kw > supply.backup_generator_kw:
        violations.append(
            f"Generator draw ({recommendation.generator_draw_kw:.1f} kW) exceeds backup capacity ({supply.backup_generator_kw:.1f} kW)."
        )

    estimated_endurance_hours = None
    if recommendation.battery_draw_kw > 0:
        estimated_endurance_hours = supply.battery_charge_kwh / recommendation.battery_draw_kw

    if estimated_endurance_hours is not None and estimated_endurance_hours < 4:
        warnings.append("Low endurance reserve: supervisor review required.")
        warnings.append(
            "Recommended actions: reduce vessel demand and/or activate backup generation to prevent service failure."
        )

    is_safe = len(violations) == 0
    safety_review = SafetyReview(
        is_safe=is_safe,
        violations=violations,
        warnings=warnings
    )

    if not is_safe:
        return EvaluationResult(
            scenario_id=scenario.scenario_id,
            status="safety_failure",
            recommendation=recommendation,
            safety_review=safety_review,
            resilience_met=False,
            estimated_endurance_hours=estimated_endurance_hours,
            summary="Proposed routing plan failed physical feasibility checks."
        )

    total_power_routed = (
        recommendation.grid_draw_kw
        + recommendation.solar_draw_kw
        + recommendation.battery_draw_kw
        + recommendation.generator_draw_kw
    )

    total_demand_kw = demand.critical_load_kw + demand.vessel_load_kw + demand.other_load_kw
    unmet_total_load_kw = max(0.0, total_demand_kw - total_power_routed)

    resilience_met = total_power_routed >= demand.critical_load_kw

    renewable_fraction = 0.0
    if total_power_routed > 0:
        renewable_fraction = min(1.0, recommendation.solar_draw_kw / total_power_routed)

    if not resilience_met:
        status = "unmet_critical_load"
        summary = (
            "Physical limits satisfied but failed to serve critical load. "
            f"Deficit: {demand.critical_load_kw - total_power_routed:.1f} kW."
        )
    elif unmet_total_load_kw > 0:
        status = "success"
        summary = (
            "Critical load is satisfied, but not all total demand is served. "
            f"Remaining unmet load: {unmet_total_load_kw:.1f} kW."
        )
    else:
        status = "success"
        summary = "Energy routing plan satisfies total operational demand within safe physical boundaries."

    if estimated_endurance_hours is not None:
        summary += f" Estimated endurance: {estimated_endurance_hours:.1f} hours."
    elif recommendation.grid_draw_kw > 0 and supply.grid_available:
        summary += " Estimated endurance: continuous while utility grid remains available."
    else:
        summary += " Estimated endurance: not available under current modeling assumptions."

    if recommendation.warnings:
        summary += f" Planner warnings: {'; '.join(recommendation.warnings)}"

    if warnings:
        summary += f" Safety actions: {'; '.join(warnings)}"

    return EvaluationResult(
        scenario_id=scenario.scenario_id,
        status=status,
        recommendation=recommendation,
        safety_review=safety_review,
        resilience_met=resilience_met,
        renewable_fraction=renewable_fraction,
        estimated_endurance_hours=estimated_endurance_hours,
        summary=summary
    )