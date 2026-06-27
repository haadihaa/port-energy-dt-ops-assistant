from app.models import Scenario, PlannerRecommendation

def compute_routing_policy(scenario: Scenario) -> PlannerRecommendation:
    """
    Computes a deterministic, resilience-first energy routing policy.
    Priority hierarchy:
    1. Critical Load (Always prioritize keeping this powered)
    2. Emissions (Prefer solar over grid/generator)
    3. Cost (Use grid if available, avoid backup generator unless necessary)
    """
    supply = scenario.supply
    demand = scenario.demand

    # Tracks allocations
    solar_to_port = 0.0
    solar_to_battery = 0.0
    grid_to_port = 0.0
    battery_to_port = 0.0
    generator_to_port = 0.0
    
    warnings = []
    
    # Calculate demand tiers
    critical_needed = demand.critical_load_kw
    vessel_needed = demand.vessel_load_kw
    other_needed = demand.other_load_kw
    
    # Total demand
    total_demand = critical_needed + vessel_needed + other_needed
    
    # Available resources
    solar_available = supply.solar_kw
    battery_available_kw = supply.battery_charge_kwh  # Assuming a 1-hour routing window
    generator_available = supply.backup_generator_kw
    
    if supply.grid_available:
        # Grid is available: Optimize for emissions and cost
        # 1. Use solar to cover as much demand as possible
        solar_to_port = min(solar_available, total_demand)
        remaining_demand = total_demand - solar_to_port
        
        # 2. Charge battery with excess solar if available
        excess_solar = solar_available - solar_to_port
        if excess_solar > 0:
            free_battery_space = max(0.0, supply.battery_max_kwh - supply.battery_charge_kwh)
            solar_to_battery = min(excess_solar, free_battery_space)
            
        # 3. Use grid to cover the remaining demand
        grid_to_port = remaining_demand
        
        rationale = "Grid is available. Served demand using solar first to minimize emissions, and utility grid for the remainder."
        priority_alignment = "Resilience is met via grid. Emissions minimized via solar offset. Battery preserved for potential outages."
    else:
        # Grid is offline: Focus strictly on resilience (critical load first)
        warnings.append("Utility grid is offline. Operating in islanded resilience mode.")
        
        # We need to satisfy critical load first, then vessel load, then other load.
        # Order of source preference under outage: Solar -> Battery -> Backup Generator
        
        # Stage 1: Satisfy Critical Load
        critical_remaining = critical_needed
        
        # Use solar for critical
        solar_for_critical = min(solar_available, critical_remaining)
        solar_to_port += solar_for_critical
        solar_available -= solar_for_critical
        critical_remaining -= solar_for_critical
        
        # Use battery for critical
        if critical_remaining > 0:
            battery_for_critical = min(battery_available_kw, critical_remaining)
            battery_to_port += battery_for_critical
            battery_available_kw -= battery_for_critical
            critical_remaining -= battery_for_critical
            
        # Use generator for critical
        if critical_remaining > 0:
            gen_for_critical = min(generator_available, critical_remaining)
            generator_to_port += gen_for_critical
            generator_available -= gen_for_critical
            critical_remaining -= gen_for_critical
            
        if critical_remaining > 0:
            warnings.append(f"CRITICAL LOAD UNMET: Deficit of {critical_remaining:.1f} kW.")
            
        # Stage 2: Satisfy Vessel Load
        vessel_remaining = vessel_needed
        
        # Use remaining solar
        solar_for_vessel = min(solar_available, vessel_remaining)
        solar_to_port += solar_for_vessel
        solar_available -= solar_for_vessel
        vessel_remaining -= solar_for_vessel
        
        # Use remaining battery
        if vessel_remaining > 0:
            battery_for_vessel = min(battery_available_kw, vessel_remaining)
            battery_to_port += battery_for_vessel
            battery_available_kw -= battery_for_vessel
            vessel_remaining -= battery_for_vessel
            
        # Use remaining generator
        if vessel_remaining > 0:
            gen_for_vessel = min(generator_available, vessel_remaining)
            generator_to_port += gen_for_vessel
            generator_available -= gen_for_vessel
            vessel_remaining -= gen_for_vessel
            
        if vessel_remaining > 0:
            warnings.append(f"Vessel demand partially shed. Unmet vessel load: {vessel_remaining:.1f} kW.")
            
        # Stage 3: Satisfy Other Load
        other_remaining = other_needed
        
        # Use remaining solar
        solar_for_other = min(solar_available, other_remaining)
        solar_to_port += solar_for_other
        solar_available -= solar_for_other
        other_remaining -= solar_for_other
        
        # Use remaining battery
        if other_remaining > 0:
            battery_for_other = min(battery_available_kw, other_remaining)
            battery_to_port += battery_for_other
            battery_available_kw -= battery_for_other
            other_remaining -= battery_for_other
            
        # Use remaining generator
        if other_remaining > 0:
            gen_for_other = min(generator_available, other_remaining)
            generator_to_port += gen_for_other
            generator_available -= gen_for_other
            other_remaining -= gen_for_other
            
        if other_remaining > 0:
            warnings.append(f"Non-critical facility load shed. Unmet: {other_remaining:.1f} kW.")
            
        # If there's still excess solar, we can charge the battery
        if solar_available > 0:
            free_battery_space = max(0.0, supply.battery_max_kwh - supply.battery_charge_kwh)
            solar_to_battery = min(solar_available, free_battery_space)
            
        rationale = "Grid offline. Dispatched local assets (solar, battery, backup generator) prioritizing critical operations first."
        priority_alignment = "Resilience prioritized by serving critical load before vessels and non-critical loads. Clean assets used before fossil generators."

    return PlannerRecommendation(
        grid_draw_kw=grid_to_port,
        solar_draw_kw=solar_to_port,
        battery_draw_kw=battery_to_port,
        generator_draw_kw=generator_to_port,
        battery_charge_kw=solar_to_battery,
        rationale=rationale,
        priority_alignment=priority_alignment,
        warnings=warnings
    )
