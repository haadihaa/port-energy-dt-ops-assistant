import os
import json
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, model_validator

from app.models import Scenario, EvaluationResult
from app.agents import run_agent_workflow


app = FastAPI(
    title="Port Energy Digital Twin Ops Assistant",
    description="A local-first, two-agent decision-support prototype for small-port energy operations.",
    version="0.1.0"
)

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
    backup_generator_kw: float = 0.0
    description: str = ""

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
            self.backup_generator_kw,
        ]

        if any(v < 0 for v in numeric_values):
            raise ValueError("All numeric inputs must be greater than or equal to 0.")

        if self.battery_max_kwh <= 0:
            raise ValueError("Battery capacity must be greater than 0.")

        if self.battery_charge_kwh > self.battery_max_kwh:
            raise ValueError("Battery level cannot exceed battery capacity.")

        return self


def load_scenarios() -> Dict[str, Scenario]:
    try:
        with open(SCENARIOS_FILE, "r") as f:
            data = json.load(f)
            return {item["scenario_id"]: Scenario(**item) for item in data}
    except Exception as e:
        raise RuntimeError(f"Failed to load sample scenarios: {e}")


scenarios_db = load_scenarios()


@app.get("/")
def read_root(request: Request):
    """Renders the dashboard operator console."""
    try:
        return templates.TemplateResponse(request, "index.html", {"request": request})
    except TypeError:
        return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Simple status check endpoint."""
    return {"status": "healthy", "service": "port-energy-ops-assistant"}


@app.get("/api/scenarios")
def list_scenarios() -> List[Dict[str, str]]:
    """Lists available scenarios with ID, name, and description."""
    return [
        {
            "scenario_id": s.scenario_id,
            "name": s.name,
            "description": s.description
        }
        for s in scenarios_db.values()
    ]


@app.get("/api/scenarios/{scenario_id}", response_model=Scenario)
def get_scenario(scenario_id: str):
    """Retrieves a single scenario by ID."""
    scenario = scenarios_db.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@app.post("/api/evaluate/{scenario_id}", response_model=EvaluationResult)
def evaluate_scenario_endpoint(scenario_id: str):
    """Runs the two-agent planning and safety evaluation workflow on a scenario."""
    scenario = scenarios_db.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    try:
        result = run_agent_workflow(scenario)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.post("/api/evaluate-custom", response_model=EvaluationResult)
def evaluate_custom_scenario(payload: CustomScenarioRequest):
    """Runs the same two-agent workflow on a user-defined scenario."""
    try:
        scenario = Scenario(
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
                "backup_generator_kw": payload.backup_generator_kw,
            },
        )
        return run_agent_workflow(scenario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")