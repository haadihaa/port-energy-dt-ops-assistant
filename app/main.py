import json
import os
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import AliasChoices, BaseModel, Field, model_validator

from app.adk.runner import run_adk_workflow
from app.agents import run_agent_workflow
from app.models import EvaluationResult, Scenario


app = FastAPI(title="Port Energy Digital Twin Ops Assistant")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_FILE = os.path.join(BASE_DIR, "data", "sample_scenarios.json")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CustomScenarioRequest(BaseModel):
    critical_load_kw: float
    vessel_load_kw: float
    other_load_kw: float = 0.0
    solar_kw: float
    battery_charge_kwh: float
    battery_max_kwh: float
    grid_available: bool
    max_grid_import_kw: float = 50.0
    backup_generator_capacity_kw: float = Field(
        20.0,
        validation_alias=AliasChoices("backup_generator_capacity_kw", "backup_generator_kw"),
    )
    backup_running_percentage: float = 0.0
    description: str = ""

    @property
    def backup_generator_kw(self) -> float:
        return self.backup_generator_capacity_kw

    @model_validator(mode="after")
    def validate_values(self):
        numeric_values = [
            self.critical_load_kw,
            self.vessel_load_kw,
            self.other_load_kw,
            self.solar_kw,
            self.battery_charge_kwh,
            self.battery_max_kwh,
            self.max_grid_import_kw,
            self.backup_generator_capacity_kw,
            self.backup_running_percentage,
        ]

        if any(v < 0 for v in numeric_values):
            raise ValueError("All numeric inputs must be greater than or equal to 0.")

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


def load_scenarios() -> Dict[str, Scenario]:
    try:
        with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["scenario_id"]: Scenario(**item) for item in data}
    except Exception as e:
        raise RuntimeError(f"Failed to load sample scenarios: {e}")


def build_custom_scenario(payload: CustomScenarioRequest) -> Scenario:
    return Scenario(
        scenario_id="custom",
        name="Custom Scenario",
        description=payload.description or "User-defined disruption scenario.",
        demand={
            "critical_load_kw": payload.critical_load_kw,
            "vessel_load_kw": payload.vessel_load_kw,
            "other_load_kw": payload.other_load_kw,
        },
        supply={
            "solar_kw": payload.solar_kw,
            "battery_charge_kwh": payload.battery_charge_kwh,
            "battery_max_kwh": payload.battery_max_kwh,
            "grid_available": payload.grid_available,
            "max_grid_import_kw": payload.max_grid_import_kw,
            "backup_generator_capacity_kw": payload.backup_generator_capacity_kw,
            "backup_running_percentage": payload.backup_running_percentage,
        },
    )


scenarios_db = load_scenarios()


@app.get("/")
def read_root(request: Request):
    try:
        return templates.TemplateResponse(request, "index.html", {"request": request})
    except TypeError:
        return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "port-energy-ops-assistant"}


@app.get("/api/scenarios")
def list_scenarios() -> List[Dict[str, str]]:
    return [
        {
            "scenario_id": s.scenario_id,
            "name": s.name,
            "description": s.description,
        }
        for s in scenarios_db.values()
    ]


@app.get("/api/scenarios/{scenario_id}", response_model=Scenario)
def get_scenario(scenario_id: str):
    scenario = scenarios_db.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@app.post("/api/evaluate/{scenario_id}", response_model=EvaluationResult)
def evaluate_scenario_endpoint(scenario_id: str):
    scenario = scenarios_db.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    try:
        return run_agent_workflow(scenario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.post("/api/evaluate-custom", response_model=EvaluationResult)
def evaluate_custom_scenario(payload: CustomScenarioRequest):
    try:
        scenario = build_custom_scenario(payload)
        return run_agent_workflow(scenario)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.post("/api/agents/evaluate/{scenario_id}")
def evaluate_scenario_with_agents(scenario_id: str):
    scenario = scenarios_db.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    try:
        return run_adk_workflow(scenario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow execution failed: {str(e)}")


@app.post("/api/agents/evaluate-custom")
def evaluate_custom_scenario_with_agents(payload: CustomScenarioRequest):
    try:
        scenario = build_custom_scenario(payload)
        return run_adk_workflow(scenario)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow execution failed: {str(e)}")