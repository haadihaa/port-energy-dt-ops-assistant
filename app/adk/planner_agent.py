from app.models import Scenario


def _read_value(container, field_name: str, default=0.0):
    if container is None:
        return default
    if isinstance(container, dict):
        return container.get(field_name, default)
    return getattr(container, field_name, default)


class OperationsPlannerAgent:
    def generate_plan(self, scenario: Scenario) -> dict:
        demand = scenario.demand
        supply = scenario.supply

        critical_load_kw = _read_value(demand, "critical_load_kw", 0.0)
        vessel_load_kw = _read_value(demand, "vessel_load_kw", 0.0)
        other_load_kw = _read_value(demand, "other_load_kw", 0.0)

        solar_kw = _read_value(supply, "solar_kw", 0.0)
        battery_charge_kwh = _read_value(supply, "battery_charge_kwh", 0.0)
        battery_max_kwh = _read_value(supply, "battery_max_kwh", 0.0)
        grid_available = _read_value(supply, "grid_available", False)
        max_grid_import_kw = _read_value(supply, "max_grid_import_kw", 0.0)
        backup_generator_capacity_kw = _read_value(supply, "backup_generator_capacity_kw", 0.0)
        backup_running_percentage = _read_value(supply, "backup_running_percentage", 0.0)

        total_demand_kw = critical_load_kw + vessel_load_kw + other_load_kw
        battery_soc_pct = 0.0
        if battery_max_kwh > 0:
            battery_soc_pct = round((battery_charge_kwh / battery_max_kwh) * 100.0, 2)

        return {
            "agent_name": "OperationsPlannerAgent",
            "role": "Propose a resilience-first operating plan for the scenario.",
            "scenario_summary": {
                "scenario_id": scenario.scenario_id,
                "name": scenario.name,
                "description": scenario.description,
            },
            "demand_snapshot": {
                "critical_load_kw": critical_load_kw,
                "vessel_load_kw": vessel_load_kw,
                "other_load_kw": other_load_kw,
                "total_demand_kw": total_demand_kw,
            },
            "supply_snapshot": {
                "solar_kw": solar_kw,
                "battery_charge_kwh": battery_charge_kwh,
                "battery_max_kwh": battery_max_kwh,
                "battery_soc_pct": battery_soc_pct,
                "grid_available": grid_available,
                "max_grid_import_kw": max_grid_import_kw,
                "backup_generator_capacity_kw": backup_generator_capacity_kw,
                "backup_running_percentage": backup_running_percentage,
            },
            "planning_policy": [
                "Use renewable energy directly first.",
                "Use grid import next when available.",
                "Use battery discharge after grid support.",
                "Use backup generation last.",
            ],
            "planner_notes": [
                "This planner layer documents the intent of the routing workflow.",
                "Final routing and validation are produced by the existing workflow engine.",
            ],
        }