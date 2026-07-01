from app.models import Scenario


def _read_value(container, field_name: str, default=0.0):
    if container is None:
        return default
    if isinstance(container, dict):
        return container.get(field_name, default)
    return getattr(container, field_name, default)


class SafetyReviewerAgent:
    def review_plan(self, scenario: Scenario, plan: dict) -> dict:
        supply = scenario.supply
        demand = scenario.demand

        battery_charge_kwh = _read_value(supply, "battery_charge_kwh", 0.0)
        battery_max_kwh = _read_value(supply, "battery_max_kwh", 0.0)
        backup_running_percentage = _read_value(supply, "backup_running_percentage", 0.0)
        backup_generator_capacity_kw = _read_value(supply, "backup_generator_capacity_kw", 0.0)
        grid_available = _read_value(supply, "grid_available", False)
        critical_load_kw = _read_value(demand, "critical_load_kw", 0.0)

        warnings = []
        escalation_triggers = []

        if battery_max_kwh <= 0:
            warnings.append("Battery capacity is zero or invalid.")
            escalation_triggers.append("Battery configuration requires review.")

        if battery_charge_kwh > battery_max_kwh:
            warnings.append("Battery charge exceeds battery capacity.")
            escalation_triggers.append("Battery state is inconsistent.")

        if backup_generator_capacity_kw > 0 and 0 < backup_running_percentage < 30:
            warnings.append("Backup generator running percentage is below minimum operating threshold.")
            escalation_triggers.append("Generator operating range requires supervision.")

        if not grid_available and critical_load_kw > 0:
            warnings.append("Grid is unavailable during a scenario with critical demand.")

        review_status = "pass" if not warnings else "review_with_caution"

        return {
            "agent_name": "SafetyReviewerAgent",
            "role": "Check feasibility, safety flags, and escalation conditions.",
            "review_status": review_status,
            "warnings": warnings,
            "escalation_triggers": escalation_triggers,
            "safety_notes": [
                "This safety layer summarizes review intent before final validation.",
                "Final safety outcome is enforced by the existing workflow and policy logic.",
            ],
            "reviewed_plan_agent": plan.get("agent_name", "unknown"),
        }