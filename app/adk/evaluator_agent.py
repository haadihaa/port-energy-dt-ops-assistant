from app.models import Scenario


class EvaluationAgent:
    def evaluate_decision(self, scenario: Scenario, plan: dict, review: dict) -> dict:
        total_demand_kw = plan.get("demand_snapshot", {}).get("total_demand_kw", 0.0)
        solar_kw = plan.get("supply_snapshot", {}).get("solar_kw", 0.0)
        battery_soc_pct = plan.get("supply_snapshot", {}).get("battery_soc_pct", 0.0)
        grid_available = plan.get("supply_snapshot", {}).get("grid_available", False)
        review_status = review.get("review_status", "unknown")

        strengths = []
        risks = []

        if solar_kw > 0:
            strengths.append("Renewable supply is available for direct support.")
        if grid_available:
            strengths.append("Grid support is available as a flexible backup path.")
        if battery_soc_pct >= 20:
            strengths.append("Battery state of charge is above a low reserve condition.")

        if total_demand_kw <= 0:
            risks.append("Demand profile appears empty or invalid.")
        if battery_soc_pct < 20:
            risks.append("Battery reserve is limited.")
        if review_status != "pass":
            risks.append("Safety review raised caution flags.")

        return {
            "agent_name": "EvaluationAgent",
            "role": "Summarize decision quality and evaluation readiness.",
            "evaluation_summary": {
                "scenario_id": scenario.scenario_id,
                "review_status": review_status,
                "strengths": strengths,
                "risks": risks,
            },
            "evaluation_notes": [
                "This layer makes the multi-agent architecture explicit for the capstone.",
                "Formal scenario evaluation can continue through the existing evaluator and eval cases.",
            ],
        }