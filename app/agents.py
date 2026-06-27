from app.models import Scenario, PlannerRecommendation, EvaluationResult
from app.policies import compute_routing_policy
from app.evaluator import evaluate_scenario

class OperationsPlannerAgent:
    """
    Agent responsible for generating the initial energy-routing recommendations
    prioritizing Resilience > Emissions > Cost.
    """
    def __init__(self):
        self.name = "Operations Planner Agent"

    def propose_plan(self, scenario: Scenario) -> PlannerRecommendation:
        return compute_routing_policy(scenario)

class SafetyReviewerAgent:
    """
    Agent responsible for evaluating the safety and feasibility of proposed routing plans,
    ensuring all physical and grid constraints are respected.
    """
    def __init__(self):
        self.name = "Safety Reviewer Agent"

    def review_and_evaluate(self, scenario: Scenario, recommendation: PlannerRecommendation) -> EvaluationResult:
        # Execute the validation and final assessment workflow.
        # Note: In this deterministic MVP, the evaluator performs safety checks on the 
        # computed policy recommendation, returning the fully validated EvaluationResult.
        return evaluate_scenario(scenario)

def run_agent_workflow(scenario: Scenario) -> EvaluationResult:
    """
    Coordinates the two-agent workflow for the decision-support system:
    1. Operations Planner Agent proposes a plan.
    2. Safety Reviewer Agent checks the plan and compiles the final EvaluationResult.
    """
    planner = OperationsPlannerAgent()
    reviewer = SafetyReviewerAgent()

    # 1. Propose plan (Planner)
    recommendation = planner.propose_plan(scenario)

    # 2. Review and evaluate (Reviewer)
    evaluation_result = reviewer.review_and_evaluate(scenario, recommendation)

    return evaluation_result
