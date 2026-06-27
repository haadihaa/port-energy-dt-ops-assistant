import os
import json
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import Scenario, EvaluationResult
from app.agents import run_agent_workflow

app = FastAPI(
    title="Port Energy Digital Twin Ops Assistant",
    description="A local-first, two-agent decision-support prototype for small-port energy operations.",
    version="0.1.0"
)

# Set up paths relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_FILE = os.path.join(BASE_DIR, "data", "sample_scenarios.json")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Configure templates and mount static files
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def load_scenarios() -> Dict[str, Scenario]:
    try:
        with open(SCENARIOS_FILE, "r") as f:
            data = json.load(f)
            # Parse into Pydantic models
            return {item["scenario_id"]: Scenario(**item) for item in data}
    except Exception as e:
        # Fallback empty list or raise configuration error
        raise RuntimeError(f"Failed to load sample scenarios: {e}")

# In-memory scenario lookup cache
scenarios_db = load_scenarios()

@app.get("/")
def read_root(request: Request):
    """Renders the dashboard operator console."""
    try:
        # Newer FastAPI/Starlette signature
        return templates.TemplateResponse(request, "index.html", {"request": request})
    except TypeError:
        # Older FastAPI/Starlette signature
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
