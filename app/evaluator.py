from app.models import Scenario, EvaluationResult, SafetyReview, PlannerRecommendation
from app.policies import compute_routing_policy

def evaluate_scenario(scenario: Scenario) -> EvaluationResult:
    """
    Evaluates a scenario by executing the planning policy and running safety and feasibility checks.
    Returns a unified EvaluationResult.
    """
    supply = scenario.supply
    demand = scenario.demand

    # Basic data validation for insufficient or invalid information
    if (supply.solar_kw < 0 or supply.battery_charge_kwh < 0 or supply.battery_max_kwh < 0 or
        supply.backup_generator_kw < 0 or demand.critical_load_kw < 0 or demand.vessel_load_kw < 0):
        return EvaluationResult(
            scenario_id=scenario.scenario_id,
            status="insufficient_information",
            resilience_met=False,
            summary="Invalid or negative capacity/demand values provided in scenario inputs."
        )

    # 1. Generate planner recommendation
    recommendation = compute_routing_policy(scenario)

    violations = []
    warnings = []

    # 2. Perform safety & feasibility checks
    # Check negative values in recommendation
    if (recommendation.grid_draw_kw < 0 or recommendation.solar_draw_kw < 0 or
        recommendation.battery_draw_kw < 0 or recommendation.generator_draw_kw < 0 or
        recommendation.battery_charge_kw < 0):
        violations.append("Recommendation contains negative energy routing values.")

    # Grid draw vs grid availability
    if recommendation.grid_draw_kw > 0 and not supply.grid_available:
        violations.append("Grid draw requested but utility grid is offline.")

    # Battery discharge vs available charge
    if recommendation.battery_draw_kw > supply.battery_charge_kwh:
        violations.append(
            f"Battery discharge draw ({recommendation.battery_draw_kw:.1f} kW) exceeds current stored charge ({supply.battery_charge_kwh:.1f} kWh)."
        )

    # Battery charge vs remaining storage space
    free_space = max(0.0, supply.battery_max_kwh - supply.battery_charge_kwh)
    if recommendation.battery_charge_kw > free_space:
        violations.append(
            f"Battery charge allocation ({recommendation.battery_charge_kw:.1f} kW) exceeds free storage capacity ({free_space:.1f} kWh)."
        )

    # Solar allocation vs available solar
    total_solar_used = recommendation.solar_draw_kw + recommendation.battery_charge_kw
    if total_solar_used > supply.solar_kw:
        violations.append(
            f"Total solar allocation ({total_solar_used:.1f} kW) exceeds available solar generation ({supply.solar_kw:.1f} kW)."
        )

    # Generator draw vs generator capacity
    if recommendation.generator_draw_kw > supply.backup_generator_kw:
        violations.append(
            f"Generator draw ({recommendation.generator_draw_kw:.1f} kW) exceeds backup capacity ({supply.backup_generator_kw:.1f} kW)."
        )

    # 3. Determine safety review status
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
            summary="Proposed routing plan failed physical feasibility checks."
        )

    # 4. Check if critical load is met
    total_power_routed = (
        recommendation.grid_draw_kw +
        recommendation.solar_draw_kw +
        recommendation.battery_draw_kw +
        recommendation.generator_draw_kw
    )
    
    resilience_met = total_power_routed >= demand.critical_load_kw

    # 5. Compute renewable fraction
    renewable_fraction = 0.0
    if total_power_routed > 0:
        # Solar is the renewable source
        renewable_fraction = min(1.0, recommendation.solar_draw_kw / total_power_routed)

    # 6. Determine final status
    if not resilience_met:
        status = "unmet_critical_load"
        summary = f"Physical limits satisfied but failed to serve critical load. Deficit: {demand.critical_load_kw - total_power_routed:.1f} kW."
    else:
        status = "success"
        summary = "Energy routing plan satisfies critical operational load within safe physical boundaries."

    # Copy planner warnings to final summary if any
    if recommendation.warnings:
        summary += f" Warnings: {'; '.join(recommendation.warnings)}"

    return EvaluationResult(
        scenario_id=scenario.scenario_id,
        status=status,
        recommendation=recommendation,
        safety_review=safety_review,
        resilience_met=resilience_met,
        renewable_fraction=renewable_fraction,
        summary=summary
    )
