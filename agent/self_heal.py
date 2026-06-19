from agent.budget import LLMBudget
from agent.llm_json import invoke_for_files
from agent.prompts import SELF_HEAL_PROMPT


def self_heal(goal: str, error: str, budget: LLMBudget) -> dict:
    budget.consume()
    return invoke_for_files(
        [
            ("system", SELF_HEAL_PROMPT),
            ("human", f"Goal:\n{goal}\n\nValidation error:\n{error}"),
        ],
        budget,
    )
