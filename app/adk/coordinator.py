from app.adk.evaluator_agent import EvaluationAgent
from app.adk.planner_agent import OperationsPlannerAgent
from app.adk.safety_agent import SafetyReviewerAgent
from app.agents import run_agent_workflow
from app.models import Scenario


class PortEnergyCoordinatorAgent:
    def __init__(self):
        self.planner = OperationsPlannerAgent()
        self.safety_reviewer = SafetyReviewerAgent()
        self.evaluator = EvaluationAgent()

    def run(self, scenario: Scenario) -> dict:
        planner_output = self.planner.generate_plan(scenario)
        safety_output = self.safety_reviewer.review_plan(scenario, planner_output)
        evaluator_output = self.evaluator.evaluate_decision(
            scenario,
            planner_output,
            safety_output,
        )

        workflow_result = run_agent_workflow(scenario)

        if hasattr(workflow_result, "model_dump"):
            serialized_result = workflow_result.model_dump()
        else:
            serialized_result = workflow_result

        return {
            "project_mode": "multi_agent_capstone",
            "agent_architecture": {
                "coordinator": "PortEnergyCoordinatorAgent",
                "sub_agents": [
                    "OperationsPlannerAgent",
                    "SafetyReviewerAgent",
                    "EvaluationAgent",
                ],
            },
            "agent_trace": {
                "planner": planner_output,
                "safety_reviewer": safety_output,
                "evaluation_agent": evaluator_output,
            },
            "final_result": serialized_result,
        }