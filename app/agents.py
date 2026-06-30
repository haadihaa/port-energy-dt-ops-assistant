from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from app.evaluator import evaluate_scenario
from app.models import EvaluationResult, PlannerRecommendation, Scenario
from app.tools.policy_tools import explain_policy, propose_deterministic_plan, recommendation_to_dict
from app.tools.scenario_tools import get_scenario_state
from app.tools.simulation_tools import simulate_dispatch, validate_constraints


class PlannerAction(BaseModel):
    source: Literal["renewables", "grid", "battery", "generator"]
    power_kw: float = Field(ge=0)
    status: Literal["on", "off", "charge", "discharge", "idle"]


class PlannerPlan(BaseModel):
    plan_id: str
    scenario_id: str
    actions: List[PlannerAction]
    expected_outcomes: Dict[str, float | int | None]
    assumptions: List[str] = Field(default_factory=list)
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


class ReviewerDecision(BaseModel):
    decision: Literal["approve", "revise", "escalate"]
    issues: List[str] = Field(default_factory=list)
    policy_flags: List[str] = Field(default_factory=list)
    review_summary: str


class OperationsPlannerAgent:
    def __init__(self) -> None:
        self.name = "Operations Planner Agent"

    def propose_plan(self, scenario: Scenario) -> Dict[str, Any]:
        scenario_state = get_scenario_state(scenario)
        policy_summary = explain_policy()
        recommendation = propose_deterministic_plan(scenario)
        simulation = simulate_dispatch(scenario, recommendation)

        planner_json = PlannerPlan(
            plan_id=f"plan-{scenario.scenario_id}-v1",
            scenario_id=scenario.scenario_id,
            actions=[
                PlannerAction(
                    source="renewables",
                    power_kw=recommendation.solar_draw_kw,
                    status="on" if recommendation.solar_draw_kw > 0 else "idle",
                ),
                PlannerAction(
                    source="grid",
                    power_kw=recommendation.grid_draw_kw + recommendation.grid_to_battery_kw,
                    status="charge"
                    if recommendation.grid_to_battery_kw > 0
                    else ("on" if recommendation.grid_draw_kw > 0 else "off"),
                ),
                PlannerAction(
                    source="battery",
                    power_kw=recommendation.battery_draw_kw + recommendation.battery_charge_kw,
                    status="discharge"
                    if recommendation.battery_draw_kw > 0
                    else ("charge" if recommendation.battery_charge_kw > 0 else "idle"),
                ),
                PlannerAction(
                    source="generator",
                    power_kw=recommendation.generator_draw_kw,
                    status="on" if recommendation.generator_draw_kw > 0 else "off",
                ),
            ],
            expected_outcomes={
                "critical_load_served_kw": min(scenario.demand.critical_load_kw, simulation["served_load_kw"]),
                "vessel_load_served_kw": max(
                    0.0,
                    min(scenario.demand.vessel_load_kw, simulation["served_load_kw"] - scenario.demand.critical_load_kw),
                ),
                "unmet_load_kw": simulation["unmet_load_kw"],
                "battery_soc_end_pct": scenario_state["supply"]["battery_soc_pct"],
                "generator_output_kw": simulation["generator_output_kw"],
                "grid_import_kw": simulation["grid_import_kw"],
                "estimated_endurance_hours": simulation["estimated_endurance_hours"] or 0.0,
                "renewable_share_pct": round((simulation["renewable_fraction"] or 0.0) * 100.0, 2),
            },
            assumptions=[
                "Deterministic routing policy remains authoritative.",
                "Battery endurance is estimated using the current prototype logic.",
                "This workflow recommends actions and does not execute controls.",
            ],
            rationale=recommendation.rationale,
            confidence=0.92 if simulation["status"] != "safety_failure" else 0.4,
        )

        return {
            "scenario_state": scenario_state,
            "policy_summary": policy_summary,
            "recommendation": recommendation,
            "recommendation_json": recommendation_to_dict(recommendation),
            "planner_json": planner_json.model_dump(),
            "planner_json_str": planner_json.model_dump_json(indent=2),
            "simulation": simulation,
        }


class SafetyReviewerAgent:
    def __init__(self) -> None:
        self.name = "Safety Reviewer Agent"

    def review_and_evaluate(
        self,
        scenario: Scenario,
        recommendation: PlannerRecommendation,
        planner_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        validation = validate_constraints(scenario, recommendation)
        simulation = simulate_dispatch(scenario, recommendation)
        evaluated = evaluate_scenario(scenario, recommendation)

        issues: List[str] = []
        policy_flags: List[str] = []

        safety_review = validation.get("safety_review") or {}
        if not validation["is_valid"]:
            issues.extend(safety_review.get("violations", []))

        if validation["estimated_endurance_hours"] is not None and validation["estimated_endurance_hours"] < 4:
            policy_flags.append("low_endurance_supervisor_review")

        if validation["status"] == "unmet_critical_load":
            decision = "escalate"
            issues.append("Critical load is not fully protected.")
        elif not validation["is_valid"]:
            decision = "revise"
        else:
            decision = "approve"

        review_summary = (
            "Plan approved after deterministic validation."
            if decision == "approve"
            else "Plan requires revision or escalation after deterministic review."
        )

        reviewer_json = ReviewerDecision(
            decision=decision,
            issues=issues,
            policy_flags=policy_flags,
            review_summary=review_summary,
        )

        final_result = EvaluationResult(
            scenario_id=scenario.scenario_id,
            status=evaluated.status,
            recommendation=recommendation,
            safety_review=evaluated.safety_review,
            resilience_met=evaluated.resilience_met,
            renewable_fraction=evaluated.renewable_fraction,
            estimated_endurance_hours=evaluated.estimated_endurance_hours,
            estimated_endurance_without_generator_hours=evaluated.estimated_endurance_without_generator_hours,
            summary=evaluated.summary,
        )

        return {
            "evaluation_result": final_result,
            "reviewer_json": reviewer_json.model_dump(),
            "reviewer_json_str": reviewer_json.model_dump_json(indent=2),
            "validation": validation,
            "simulation": simulation,
            "planner_payload": planner_payload,
        }


def run_agent_workflow(scenario: Scenario) -> EvaluationResult:
    planner = OperationsPlannerAgent()
    reviewer = SafetyReviewerAgent()

    planner_payload = planner.propose_plan(scenario)
    recommendation: PlannerRecommendation = planner_payload["recommendation"]
    reviewed = reviewer.review_and_evaluate(scenario, recommendation, planner_payload)
    result: EvaluationResult = reviewed["evaluation_result"]

    decision = reviewed["reviewer_json"]["decision"]
    review_summary = reviewed["reviewer_json"]["review_summary"]

    if decision == "approve":
        result.summary = f"{result.summary} Reviewer decision: approve. {review_summary}"
    elif decision == "revise":
        result.summary = f"{result.summary} Reviewer decision: revise. {review_summary}"
    else:
        result.status = "unmet_critical_load"
        result.summary = f"{result.summary} Reviewer decision: escalate. {review_summary}"

    return result