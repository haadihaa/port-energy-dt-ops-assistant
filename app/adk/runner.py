from app.adk.coordinator import PortEnergyCoordinatorAgent
from app.models import Scenario


def run_adk_workflow(scenario: Scenario) -> dict:
    coordinator = PortEnergyCoordinatorAgent()
    return coordinator.run(scenario)