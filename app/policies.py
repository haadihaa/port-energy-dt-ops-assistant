from app.models import PlannerRecommendation, Scenario


ENDURANCE_ESCALATION_HOURS = 4.0


def _generator_capacity_kw(supply) -> float:
    return max(
        0.0,
        getattr(supply, "backup_generator_capacity_kw", getattr(supply, "backup_generator_kw", 0.0)),
    )


def _generator_min_operating_kw(supply) -> float:
    return max(0.0, getattr(supply, "generator_min_operating_kw", 0.3 * _generator_capacity_kw(supply)))


def _generator_running_percentage(supply) -> float:
    return max(0.0, getattr(supply, "backup_running_percentage", 0.0))


def compute_routing_policy(scenario: Scenario) -> PlannerRecommendation:
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
    generator_available_kw = _generator_capacity_kw(supply)
    generator_min_operating_kw = _generator_min_operating_kw(supply)
    generator_running_percentage = _generator_running_percentage(supply)

    if not supply.grid_available:
        warnings.append("Utility grid is offline. Operating in islanded resilience mode.")

    solar_to_port = min(solar_available, total_demand)
    solar_available -= solar_to_port
    remaining_demand = total_demand - solar_to_port

    if remaining_demand > 0 and supply.grid_available:
        grid_to_port = min(remaining_demand, grid_limit_kw)
        remaining_demand -= grid_to_port

    remaining_grid_headroom = max(0.0, grid_limit_kw - grid_to_port) if supply.grid_available else 0.0
    battery_room_to_target = max(0.0, target_battery_kwh - supply.battery_charge_kwh)

    if remaining_demand <= 0 and solar_available > 0 and battery_room_to_target > 0:
        solar_to_battery = min(solar_available, battery_room_to_target)
        solar_available -= solar_to_battery
        battery_room_to_target -= solar_to_battery

    if remaining_demand <= 0 and remaining_grid_headroom > 0 and battery_room_to_target > 0:
        grid_to_battery = min(remaining_grid_headroom, battery_room_to_target)
        remaining_grid_headroom -= grid_to_battery
        battery_room_to_target -= grid_to_battery

    if remaining_demand <= 0 and solar_available > 0:
        if supply.grid_available:
            grid_export_kw = solar_available
        else:
            warnings.append(
                f"Surplus renewable energy of {solar_available:.1f} kW cannot be exported because the grid is offline."
            )

    if remaining_demand > 0 and generator_available_kw > 0:
        projected_battery_draw_kw = min(remaining_demand, battery_available_kwh)
        projected_endurance_hours = None

        if projected_battery_draw_kw > 0:
            projected_endurance_hours = battery_available_kwh / projected_battery_draw_kw

        should_preserve_battery = (
            projected_endurance_hours is not None
            and projected_endurance_hours < ENDURANCE_ESCALATION_HOURS
        )

        if should_preserve_battery:
            proposed_generator_kw = min(remaining_demand, generator_available_kw)

            if proposed_generator_kw >= generator_min_operating_kw:
                generator_to_port = proposed_generator_kw
                remaining_demand -= generator_to_port

                if abs(generator_to_port - generator_available_kw) < 1e-9:
                    warnings.append(
                        f"Backup generator should run at 100% of available capacity ({generator_to_port:.1f} kW) "
                        "to preserve battery endurance."
                    )
                else:
                    pct = (generator_to_port / generator_available_kw) * 100 if generator_available_kw > 0 else 0
                    warnings.append(
                        f"Backup generator should run at {pct:.0f}% of available capacity "
                        f"({generator_to_port:.1f} kW) to preserve battery endurance."
                    )
            else:
                warnings.append(
                    "Backup generator was not dispatched because the required output "
                    f"({proposed_generator_kw:.1f} kW) is below the minimum stable operating threshold "
                    f"({generator_min_operating_kw:.1f} kW)."
                )

    if remaining_demand > 0:
        battery_to_port = min(remaining_demand, battery_available_kwh)
        remaining_demand -= battery_to_port
        battery_available_kwh -= battery_to_port

    if remaining_demand > 0 and generator_available_kw > generator_to_port:
        additional_generator_headroom = generator_available_kw - generator_to_port
        proposed_generator_kw = min(remaining_demand, additional_generator_headroom)

        if generator_to_port == 0 and proposed_generator_kw < generator_min_operating_kw:
            warnings.append(
                "Backup generator was not dispatched because the required output "
                f"({proposed_generator_kw:.1f} kW) is below the minimum stable operating threshold "
                f"({generator_min_operating_kw:.1f} kW)."
            )
        elif proposed_generator_kw > 0:
            generator_to_port += proposed_generator_kw
            remaining_demand -= proposed_generator_kw

    if generator_running_percentage > 0 and generator_to_port == 0:
        warnings.append(
            "Backup generator is currently running but is not required by the recommended plan; operator should shut it down."
        )

    total_served = solar_to_port + grid_to_port + battery_to_port + generator_to_port
    unmet_total_load = max(0.0, total_demand - total_served)
    critical_deficit = max(0.0, demand.critical_load_kw - total_served)

    if unmet_total_load > 0:
        warnings.append(f"Demand not fully satisfied. Unmet total load: {unmet_total_load:.1f} kW.")

    if critical_deficit > 0:
        warnings.append(f"CRITICAL LOAD UNMET: Deficit of {critical_deficit:.1f} kW.")

    if generator_to_port > 0 and battery_to_port > 0:
        rationale = (
            "Served demand using solar and grid first, then dispatched the backup generator to protect battery endurance, "
            "with the battery covering only the remaining residual load."
        )
    elif generator_to_port > 0:
        rationale = (
            "Served demand using solar and grid first, then dispatched the backup generator to preserve resilience and avoid unnecessary battery depletion."
        )
    elif total_served >= total_demand and grid_export_kw > 0 and (solar_to_battery > 0 or grid_to_battery > 0):
        rationale = (
            "Served all demand using direct renewable energy first, kept backup generation off, "
            "charged the battery toward the 80% target, and exported the remaining surplus to the grid."
        )
    elif total_served >= total_demand and grid_export_kw > 0:
        rationale = (
            "Served all demand using direct renewable energy first, kept backup generation off, "
            "and exported the remaining surplus to the grid."
        )
    elif total_served >= total_demand and (solar_to_battery > 0 or grid_to_battery > 0):
        rationale = "Served all demand first, then charged the battery toward the 80% operating target."
    else:
        rationale = (
            "Attempted to satisfy demand using renewable energy first, then grid import, "
            "then battery discharge, then backup generation as a last resort."
        )

    priority_alignment = (
        "Resilience first by serving demand as far as possible; renewable energy is used directly before other sources; "
        "generator support is enabled before deep battery depletion when endurance would fall below the escalation threshold; "
        "battery is preserved for sustained operations and restored toward the 80% operating target when possible."
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
        warnings=warnings,
    )