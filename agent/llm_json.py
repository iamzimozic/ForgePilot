from rich.console import Console

from agent.budget import LLMBudget
from agent.json_utils import extract_json
from agent.llm import get_llm

console = Console()

JSON_RETRY_HINT = (
    "Your previous reply was invalid JSON (often caused by literal newlines inside strings). "
    "Return ONLY valid JSON. Every file body must use \\n for line breaks inside quoted strings."
)


def invoke_for_files(messages: list, budget: LLMBudget) -> dict:
    """Call the LLM and parse a { \"files\": ... } JSON payload, with one JSON retry."""
    llm = get_llm()

    try:
        response = llm.invoke(messages)
        return extract_json(response.content)
    except ValueError as e:
        if "JSON" not in str(e) and "json" not in str(e).lower():
            raise
        if budget.remaining <= 0:
            raise
        console.print("[yellow]Invalid JSON — retrying once with stricter format hint[/yellow]")
        budget.consume()
        retry_messages = messages + [
            ("assistant", "Invalid JSON output."),
            ("human", JSON_RETRY_HINT),
        ]
        response = llm.invoke(retry_messages)
        return extract_json(response.content)
