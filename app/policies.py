from app.models import Scenario, PlannerRecommendation


def compute_routing_policy(scenario: Scenario) -> PlannerRecommendation:
    """
    Routing logic:
    1. Satisfy total port demand.
    2. Use renewable energy directly first.
    3. If there is a remaining deficit: Grid -> Battery -> Backup Generator.
    4. If there is a surplus after serving demand:
       - keep generator off,
       - charge battery toward the 80% target,
       - export the remainder to the grid.
    5. If renewable < total demand but renewable + allowed grid import can exceed demand,
       use remaining grid headroom to charge battery toward the 80% target before generator use.
    6. Backup generator model:
       - rated by backup_generator_capacity_kw,
       - current operating point provided by backup_running_percentage,
       - if generator is used, it cannot run below 30% of rated capacity,
       - if minimum backup output would oversupply demand, cut the difference from grid import first.
    """
    supply = scenario.supply
    demand = scenario.demand

    solar_to_port = 0.0
    solar_to_battery = 0.0
    grid_to_port = 0.0
    grid_to_battery = 0.0
    battery_to_port = 0.0
    generator_to_port = 0.0
    grid_export_kw = 0.0

    warnings = []

    total_demand = demand.critical_load_kw + demand.vessel_load_kw + demand.other_load_kw
    target_battery_kwh = 0.8 * supply.battery_max_kwh

    solar_available = max(0.0, supply.solar_kw)
    battery_available_kwh = max(0.0, supply.battery_charge_kwh)
    grid_limit_kw = max(0.0, supply.max_grid_import_kw) if supply.grid_available else 0.0

    generator_capacity_kw = max(0.0, supply.backup_generator_capacity_kw)
    generator_running_pct = max(0.0, supply.backup_running_percentage)
    generator_min_kw = 0.3 * generator_capacity_kw if generator_capacity_kw > 0 else 0.0

    if not supply.grid_available:
        warnings.append("Utility grid is offline. Operating in islanded resilience mode.")

    if generator_running_pct > 0:
        warnings.append(
            f"Backup generator is currently operating at {generator_running_pct:.1f}% of rated capacity."
        )

    solar_to_port = min(solar_available, total_demand)
    solar_available -= solar_to_port
    remaining_demand = total_demand - solar_to_port

    if remaining_demand > 0 and supply.grid_available:
        grid_to_port = min(remaining_demand, grid_limit_kw)
        remaining_demand -= grid_to_port

    remaining_grid_headroom = max(0.0, grid_limit_kw - grid_to_port) if supply.grid_available else 0.0
    battery_room_to_target = max(0.0, target_battery_kwh - supply.battery_charge_kwh)

    if solar_available > 0 and battery_room_to_target > 0:
        solar_to_battery = min(solar_available, battery_room_to_target)
        solar_available -= solar_to_battery
        battery_room_to_target -= solar_to_battery

    if remaining_demand <= 0 and solar_available > 0:
        if supply.grid_available:
            grid_export_kw = solar_available
        else:
            warnings.append(
                f"Surplus renewable energy of {solar_available:.1f} kW cannot be exported because the grid is offline."
            )

    if remaining_demand > 0 and remaining_grid_headroom > 0 and battery_room_to_target > 0:
        grid_to_battery = min(remaining_grid_headroom, battery_room_to_target)
        remaining_grid_headroom -= grid_to_battery
        battery_room_to_target -= grid_to_battery

    if remaining_demand > 0:
        battery_to_port = min(remaining_demand, battery_available_kwh)
        remaining_demand -= battery_to_port
        battery_available_kwh -= battery_to_port

    if remaining_demand > 0 and generator_capacity_kw > 0:
        if remaining_demand < generator_min_kw:
            grid_reduction_needed = generator_min_kw - remaining_demand

            if grid_to_port > 0:
                grid_reduction = min(grid_to_port, grid_reduction_needed)
                grid_to_port -= grid_reduction
                remaining_demand += grid_reduction
                grid_reduction_needed -= grid_reduction

            if grid_reduction_needed > 0 and battery_to_port > 0:
                battery_reduction = min(battery_to_port, grid_reduction_needed)
                battery_to_port -= battery_reduction
                remaining_demand += battery_reduction
                grid_reduction_needed -= battery_reduction

            generator_to_port = min(generator_min_kw, generator_capacity_kw)
            remaining_demand -= generator_to_port

            if grid_reduction_needed > 0:
                warnings.append(
                    "Backup generator minimum loading required reducing other sources, and some excess generation may remain unavoidable."
                )
        else:
            generator_to_port = min(remaining_demand, generator_capacity_kw)
            remaining_demand -= generator_to_port

    total_served = solar_to_port + grid_to_port + battery_to_port + generator_to_port
    unmet_total_load = max(0.0, total_demand - total_served)
    critical_deficit = max(0.0, demand.critical_load_kw - total_served)

    if unmet_total_load > 0:
        warnings.append(f"Demand not fully satisfied. Unmet total load: {unmet_total_load:.1f} kW.")

    if critical_deficit > 0:
        warnings.append(f"CRITICAL LOAD UNMET: Deficit of {critical_deficit:.1f} kW.")

    if generator_to_port > 0 and generator_to_port < generator_min_kw:
        warnings.append(
            "Backup generator dispatch is below the 30% minimum operational threshold."
        )

    if total_served >= total_demand and grid_export_kw > 0 and (solar_to_battery > 0 or grid_to_battery > 0):
        rationale = (
            "Served all demand using direct renewable energy first, kept backup generation off when not needed, "
            "charged the battery toward the 80% target, and exported the remaining surplus to the grid."
        )
    elif total_served >= total_demand and grid_export_kw > 0:
        rationale = (
            "Served all demand using direct renewable energy first, kept backup generation off when not needed, "
            "and exported the remaining surplus to the grid."
        )
    elif total_served >= total_demand and (solar_to_battery > 0 or grid_to_battery > 0):
        rationale = (
            "Served all demand first, then charged the battery toward the 80% operating target."
        )
    else:
        rationale = (
            "Attempted to satisfy demand using renewable energy first, then grid import, "
            "then battery discharge, then backup generation while respecting the minimum operational loading rule."
        )

    priority_alignment = (
        "Resilience first by serving demand as far as possible; renewable energy is used directly before other sources; "
        "battery is restored toward the 80% operating target when possible; backup generation remains the last source "
        "and must respect minimum operational loading."
    )

    return PlannerRecommendation(
        grid_draw_kw=grid_to_port,
        solar_draw_kw=solar_to_port,
        battery_draw_kw=battery_to_port,
        generator_draw_kw=generator_to_port,
        battery_charge_kw=solar_to_battery,
        grid_to_battery_kw=grid_to_battery,
        grid_export_kw=grid_export_kw,
        rationale=rationale,
        priority_alignment=priority_alignment,
        warnings=warnings
    )