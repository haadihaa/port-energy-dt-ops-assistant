from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class EnergySupplyState(BaseModel):
    solar_kw: float = Field(..., description="Available solar generation capacity in kW")
    battery_charge_kwh: float = Field(..., description="Current battery storage level in kWh")
    battery_max_kwh: float = Field(..., description="Total battery capacity in kWh")
    grid_available: bool = Field(True, description="Indicates if utility grid power is online")
    backup_generator_kw: float = Field(0.0, description="Available backup generator capacity in kW")


class EnergyDemandInput(BaseModel):
    critical_load_kw: float = Field(..., description="Minimum load required to maintain safe port operations in kW")
    vessel_load_kw: float = Field(..., description="Requested vessel shore power demand in kW")
    other_load_kw: float = Field(0.0, description="Non-critical auxiliary port load in kW")


class Scenario(BaseModel):
    scenario_id: str = Field(..., description="Unique scenario identifier")
    name: str = Field(..., description="Name of the scenario")
    description: str = Field("", description="Context/disruption details")
    supply: EnergySupplyState = Field(..., description="Input supply capabilities")
    demand: EnergyDemandInput = Field(..., description="Input demand requirements")


class PlannerRecommendation(BaseModel):
    grid_draw_kw: float = Field(0.0, description="Power to draw from the utility grid in kW")
    solar_draw_kw: float = Field(0.0, description="Power to draw directly from solar in kW")
    battery_draw_kw: float = Field(0.0, description="Power to discharge from the battery in kW")
    generator_draw_kw: float = Field(0.0, description="Power to draw from backup generator in kW")
    battery_charge_kw: float = Field(0.0, description="Power allocated to charge the battery in kW")
    rationale: str = Field(..., description="Brief reasoning behind the routing plan")
    priority_alignment: str = Field(..., description="How this plan satisfies resilience > emissions > cost")
    warnings: List[str] = Field(default_factory=list, description="Any potential operational risks flagged by the planner")


class SafetyReview(BaseModel):
    is_safe: bool = Field(..., description="True if recommendations do not violate physical boundaries or rates")
    violations: List[str] = Field(default_factory=list, description="List of physical boundary violations")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking safety warnings or edge cases flagged")


class EvaluationResult(BaseModel):
    scenario_id: str = Field(..., description="Associated scenario ID")
    status: str = Field(..., description="Overall evaluation status (e.g., success, unmet_critical_load, safety_failure, insufficient_information)")
    recommendation: Optional[PlannerRecommendation] = Field(None, description="The evaluated routing plan, if available")
    safety_review: Optional[SafetyReview] = Field(None, description="The completed safety review, if available")
    resilience_met: bool = Field(False, description="True if critical load is fully satisfied")
    renewable_fraction: float = Field(0.0, description="Estimated share of total powered load that came from solar (0.0 to 1.0)")
    summary: str = Field(..., description="Brief outcome summary of the scenario evaluation")