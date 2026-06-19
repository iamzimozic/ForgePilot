from agent.budget import LLMBudget
from agent.llm_json import invoke_for_files
from agent.prompts import GENERATION_PROMPT

_WEB_KEYWORDS = (
    "web", "webpage", "website", "html", "css", "javascript", "js",
    "browser", "ui", "frontend", "calculator", "page", "dom",
)


def _build_human_message(goal: str) -> str:
    lower = goal.lower()
    parts = [goal]

    if any(word in lower for word in _WEB_KEYWORDS):
        parts.append(
            "\n\nAdditional requirements for this web/UI goal:\n"
            "- Include index.html (and .css / .js if needed) for the UI.\n"
            "- Include at least one test_*.py (e.g. test_web.py) that verifies "
            "the page (HTML structure, required buttons/inputs, or served routes).\n"
            "- Do not return only static assets without Python tests."
        )

    parts.append(
        "\n\nMandatory: include at least one file named test_*.py in the `files` object."
    )
    return "".join(parts)


def generate_project(goal: str, budget: LLMBudget) -> dict:
    budget.consume()
    return invoke_for_files(
        [
            ("system", GENERATION_PROMPT),
            ("human", _build_human_message(goal)),
        ],
        budget,
    )
