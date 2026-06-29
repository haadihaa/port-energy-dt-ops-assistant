Feature: Hybrid multi-agent port energy resilience planning
  The system supports disruption-aware energy routing for port operations.
  A Planner Agent proposes a dispatch plan, deterministic tools validate it,
  and a Reviewer Agent approves, revises, or escalates the recommendation.

  Background:
    Given the system supports predefined and custom disruption scenarios
    And routing follows a resilience-first policy
    And deterministic safety constraints must be enforced outside the model

  @routing @renewables
  Scenario: Use renewable energy first when solar can fully serve demand
    Given a scenario with critical load 20 kW
    And vessel load 10 kW
    And other load 0 kW
    And solar supply 40 kW
    And battery state of charge 80 percent
    And grid is available with max import 50 kW
    And backup generator rated capacity is 60 kW
    When the Planner Agent proposes a dispatch plan
    Then solar should serve the full 30 kW demand first
    And grid import should be 0 kW
    And battery discharge should be 0 kW
    And generator output should be 0 kW
    And the Reviewer Agent should approve the plan

  @routing @grid
  Scenario: Use grid import before battery during a deficit when grid is online
    Given a scenario with critical load 40 kW
    And vessel load 20 kW
    And other load 0 kW
    And solar supply 10 kW
    And battery state of charge 80 percent
    And grid is available with max import 50 kW
    And backup generator rated capacity is 100 kW
    When the Planner Agent proposes a dispatch plan
    Then solar should be used first
    And grid import should be used before battery discharge
    And battery discharge should remain 0 kW if the grid can cover the remaining demand
    And the Reviewer Agent should approve the plan

  @routing @battery
  Scenario: Use battery after grid when online deficit exceeds renewable plus grid supply
    Given a scenario with critical load 50 kW
    And vessel load 30 kW
    And other load 0 kW
    And solar supply 10 kW
    And battery state of charge 80 percent
    And grid is available with max import 30 kW
    And backup generator rated capacity is 80 kW
    When the Planner Agent proposes a dispatch plan
    Then solar should be used first
    And grid import should be used up to the configured cap
    And battery discharge should be used before backup generation when additional energy is still needed
    And the Reviewer Agent should approve the plan

  @routing @generator
  Scenario: Use backup generation last when renewables, grid, and battery are insufficient
    Given a scenario with critical load 50 kW
    And vessel load 40 kW
    And other load 10 kW
    And solar supply 5 kW
    And battery state of charge 20 percent
    And grid is available with max import 20 kW
    And backup generator rated capacity is 120 kW
    When the Planner Agent proposes a dispatch plan
    Then solar should be used first
    And grid import should be used next
    And battery discharge should be used before the generator
    And the backup generator should only cover the remaining unmet demand
    And the Reviewer Agent should approve the plan

  @surplus @battery_target
  Scenario: Charge the battery toward the 80 percent target before exporting surplus
    Given a scenario with critical load 10 kW
    And vessel load 10 kW
    And other load 0 kW
    And solar supply 50 kW
    And battery state of charge 40 percent
    And grid is available with max import 50 kW
    And backup generator rated capacity is 60 kW
    When the Planner Agent proposes a dispatch plan
    Then solar should serve port demand first
    And battery charging should occur before grid export
    And backup generation should remain off
    And the Reviewer Agent should approve the plan

  @surplus @generator_off
  Scenario: Turn off backup generation before exporting excess energy
    Given a scenario with critical load 20 kW
    And vessel load 10 kW
    And other load 0 kW
    And solar supply 60 kW
    And battery state of charge 85 percent
    And grid is available with max import 50 kW
    And backup generator rated capacity is 100 kW
    And the backup generator is initially running
    When the Planner Agent proposes a dispatch plan
    Then the plan should turn off backup generation when it is not required
    And any remaining surplus should be exported only after battery target logic is satisfied
    And the Reviewer Agent should approve the plan

  @constraint @generator_minimum
  Scenario: Reject generator dispatch below 30 percent of rated capacity
    Given a scenario with critical load 30 kW
    And vessel load 20 kW
    And other load 0 kW
    And solar supply 10 kW
    And battery state of charge 80 percent
    And grid is not available
    And backup generator rated capacity is 100 kW
    When the Planner Agent proposes generator output below 30 kW
    Then validate_constraints should reject the plan
    And the Reviewer Agent should return revise or escalate
    And the review summary should mention the minimum operating threshold

  @constraint @grid_cap
  Scenario: Enforce maximum grid import in grid-on mode
    Given a scenario with critical load 50 kW
    And vessel load 30 kW
    And other load 0 kW
    And solar supply 5 kW
    And battery state of charge 80 percent
    And grid is available with max import 25 kW
    And backup generator rated capacity is 100 kW
    When the Planner Agent proposes a dispatch plan
    Then grid import must not exceed 25 kW
    And any remaining deficit must be handled by battery discharge before backup generation
    And the Reviewer Agent should reject any plan that exceeds the grid cap

  @reviewer @safety
  Scenario: Reviewer rejects an unsafe planner proposal
    Given a scenario with critical load 40 kW
    And vessel load 30 kW
    And other load 0 kW
    And solar supply 0 kW
    And battery state of charge 10 percent
    And grid is not available
    And backup generator rated capacity is 50 kW
    When the Planner Agent proposes a plan that violates a hard constraint
    Then the Reviewer Agent should return revise or escalate
    And the issues list should describe the violated constraint
    And the final recommendation should not be marked approved

  @revision @workflow
  Scenario: Planner revises a rejected plan once using reviewer feedback
    Given a scenario where the initial planner proposal is rejected by the Reviewer Agent
    When the reviewer returns actionable feedback
    Then the Planner Agent should generate one revised plan
    And the revised plan should be revalidated with deterministic tools
    And the workflow should stop after one retry or a final escalation

  @escalation @unmet_load
  Scenario: Escalate when no feasible plan can fully protect critical load
    Given a scenario with critical load 80 kW
    And vessel load 30 kW
    And other load 10 kW
    And solar supply 0 kW
    And battery state of charge 5 percent
    And grid is not available
    And backup generator rated capacity is 20 kW
    When the Planner Agent evaluates the scenario
    Then the system should identify unmet critical load risk
    And the Reviewer Agent should escalate the case
    And the operator should be warned that supervisor attention is required

  @custom @input
  Scenario: Support custom disruption scenarios entered by the operator
    Given an operator submits a custom scenario through the application
    When the scenario passes numeric validation
    Then the system should evaluate it using the same planner and reviewer workflow
    And the result should include routing, rationale, review notes, and endurance output

  @predefined @input
  Scenario: Support predefined disruption scenarios from the sample dataset
    Given the application loads sample scenarios from the bundled JSON file
    When a user selects a predefined scenario
    Then the system should evaluate that scenario using the same workflow used for custom scenarios
    And the response should include a structured recommendation

  @tools @agentic
  Scenario: Planner uses tools before finalizing a plan
    Given a valid disruption scenario
    When the Planner Agent is asked for a recommendation
    Then it should call get_scenario_state before finalizing the plan
    And it should call simulate_dispatch to estimate outcomes
    And it should call validate_constraints before submitting the plan for review

  @evaluation @consistency
  Scenario: Reviewer decision is consistent with deterministic validation results
    Given a valid planner proposal and its validation output
    When the Reviewer Agent checks the plan
    Then it should not approve a plan that deterministic validation marks invalid
    And it should approve or revise based on the same validated evidence

  @policy @hitl
  Scenario: Human approval is required for any future execution-like action
    Given a plan has been approved for recommendation
    When a downstream action would change a real operating system state
    Then the policy layer must block automatic execution
    And the system must require explicit human confirmation