import json
import re
from rich.console import Console

console = Console()


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1)
        text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()


def _escape_control_chars_in_json_strings(s: str) -> str:
    """
    Repair LLM output where file contents use literal newlines inside JSON strings.
    Only transforms characters while inside a double-quoted JSON string.
    """
    out = []
    in_string = False
    escape = False
    i = 0
    while i < len(s):
        ch = s[i]
        if escape:
            out.append(ch)
            escape = False
            i += 1
            continue
        if ch == "\\" and in_string:
            out.append(ch)
            escape = True
            i += 1
            continue
        if ch == '"':
            in_string = not in_string
            out.append(ch)
            i += 1
            continue
        if in_string:
            if ch == "\n":
                out.append("\\n")
                i += 1
                continue
            if ch == "\r":
                if i + 1 < len(s) and s[i + 1] == "\n":
                    out.append("\\n")
                    i += 2
                else:
                    out.append("\\r")
                    i += 1
                continue
            if ch == "\t":
                out.append("\\t")
                i += 1
                continue
            if ord(ch) < 32:
                out.append(f"\\u{ord(ch):04x}")
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def _parse_json_object(json_str: str) -> dict:
    for attempt, candidate in enumerate((json_str, _escape_control_chars_in_json_strings(json_str))):
        try:
            data = json.loads(candidate)
            if attempt == 1:
                console.print("[yellow]✓ JSON repaired (escaped multiline strings)[/yellow]")
            return data
        except json.JSONDecodeError:
            continue
    raise ValueError("❌ JSON parsing failed after repair attempt")


def extract_json(text: str) -> dict:
    console.rule("[bold cyan]Raw LLM Output")
    console.print(text)

    text = _strip_markdown_fences(text)
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or start >= end:
        raise ValueError("❌ No JSON object found in LLM output")

    data = _parse_json_object(text[start : end + 1])

    if not isinstance(data, dict):
        raise ValueError("❌ Parsed JSON is not a dict")

    if "files" not in data:
        raise ValueError("❌ JSON missing required top-level key: 'files'")

    if not isinstance(data["files"], dict):
        raise ValueError("❌ 'files' must be a dictionary")

    console.print("[green]✓ JSON extracted and validated[/green]")
    return data
