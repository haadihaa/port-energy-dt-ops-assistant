from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class EnergySupplyState(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    solar_kw: float = Field(..., description="Available solar generation capacity in kW")
    battery_charge_kwh: float = Field(..., description="Current battery storage level in kWh")
    battery_max_kwh: float = Field(..., description="Total battery capacity in kWh")
    grid_available: bool = Field(True, description="Indicates if utility grid power is online")
    max_grid_import_kw: float = Field(50.0, description="Maximum allowed utility grid import in kW")
    backup_generator_capacity_kw: float = Field(
        0.0,
        validation_alias=AliasChoices("backup_generator_capacity_kw", "backup_generator_kw"),
        description="Rated backup generator capacity in kW",
    )
    backup_running_percentage: float = Field(
        0.0,
        description="Current generator running level as a percentage of rated capacity",
    )

    @property
    def backup_generator_kw(self) -> float:
        return self.backup_generator_capacity_kw

    @property
    def generator_min_operating_kw(self) -> float:
        if self.backup_generator_capacity_kw <= 0:
            return 0.0
        return 0.3 * self.backup_generator_capacity_kw

    @property
    def generator_running_kw(self) -> float:
        if self.backup_generator_capacity_kw <= 0 or self.backup_running_percentage <= 0:
            return 0.0
        return (self.backup_generator_capacity_kw * self.backup_running_percentage) / 100.0

    @model_validator(mode="after")
    def validate_values(self):
        numeric_values = [
            self.solar_kw,
            self.battery_charge_kwh,
            self.battery_max_kwh,
            self.max_grid_import_kw,
            self.backup_generator_capacity_kw,
            self.backup_running_percentage,
        ]

        if any(v < 0 for v in numeric_values):
            raise ValueError("All supply values must be greater than or equal to 0.")

        if self.battery_max_kwh <= 0:
            raise ValueError("Battery capacity must be greater than 0.")

        if self.battery_charge_kwh > self.battery_max_kwh:
            raise ValueError("Battery level cannot exceed battery capacity.")

        if self.backup_running_percentage > 100:
            raise ValueError("Backup generator running percentage must be between 0 and 100.")

        if (
            self.backup_running_percentage > 0
            and self.backup_running_percentage < 30
            and self.backup_generator_capacity_kw > 0
        ):
            raise ValueError(
                "Backup generator running percentage must be 0 or at least 30 when the generator is in use."
            )

        return self


class EnergyDemandInput(BaseModel):
    critical_load_kw: float = Field(..., description="Minimum load required to maintain safe port operations in kW")
    vessel_load_kw: float = Field(..., description="Requested vessel shore power demand in kW")
    other_load_kw: float = Field(0.0, description="Non-critical auxiliary port load in kW")

    @model_validator(mode="after")
    def validate_values(self):
        numeric_values = [
            self.critical_load_kw,
            self.vessel_load_kw,
            self.other_load_kw,
        ]

        if any(v < 0 for v in numeric_values):
            raise ValueError("All demand values must be greater than or equal to 0.")

        return self


class Scenario(BaseModel):
    scenario_id: str = Field(..., description="Unique scenario identifier")
    name: str = Field(..., description="Name of the scenario")
    description: str = Field("", description="Context/disruption details")
    supply: EnergySupplyState = Field(..., description="Input supply capabilities")
    demand: EnergyDemandInput = Field(..., description="Input demand requirements")


class PlannerRecommendation(BaseModel):
    grid_draw_kw: float = Field(0.0, description="Power to draw from the utility grid to the port in kW")
    solar_draw_kw: float = Field(0.0, description="Power to draw directly from solar to the port in kW")
    battery_draw_kw: float = Field(0.0, description="Power to discharge from the battery to the port in kW")
    generator_draw_kw: float = Field(0.0, description="Power to draw from backup generator to the port in kW")
    battery_charge_kw: float = Field(0.0, description="Power allocated from solar to charge the battery in kW")
    grid_to_battery_kw: float = Field(0.0, description="Power allocated from the grid to charge the battery in kW")
    grid_export_kw: float = Field(0.0, description="Power exported from the port back to the utility grid in kW")
    rationale: str = Field(..., description="Brief reasoning behind the routing plan")
    priority_alignment: str = Field(..., description="How this plan satisfies resilience > emissions > cost")
    warnings: List[str] = Field(default_factory=list, description="Any potential operational risks flagged by the planner")


class SafetyReview(BaseModel):
    is_safe: bool = Field(..., description="True if recommendations do not violate physical boundaries or rates")
    violations: List[str] = Field(default_factory=list, description="List of physical boundary violations")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking safety warnings or edge cases flagged")


class EvaluationResult(BaseModel):
    scenario_id: str = Field(..., description="Associated scenario ID")
    status: str = Field(..., description="Overall evaluation status")
    recommendation: Optional[PlannerRecommendation] = Field(None, description="The evaluated routing plan, if available")
    safety_review: Optional[SafetyReview] = Field(None, description="The completed safety review, if available")
    resilience_met: bool = Field(False, description="True if critical load is fully satisfied")
    renewable_fraction: float = Field(0.0, description="Estimated share of total powered load that came from solar")
    estimated_endurance_hours: Optional[float] = Field(
        None,
        description="Estimated endurance in hours under the recommended routed operating condition",
    )
    estimated_endurance_without_generator_hours: Optional[float] = Field(
        None,
        description="Estimated endurance in hours if the backup generator is not used",
    )
    summary: str = Field(..., description="Brief outcome summary of the scenario evaluation")