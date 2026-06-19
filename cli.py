import sys
from rich.console import Console

from config import WORKSPACE_DIR, MAX_LLM_CALLS
from agent.normalize import normalize_command
from agent.cache import (
    load_cached,
    save_cached,
    load_last_good,
    save_last_good,
)
from agent.generator import generate_project
from agent.self_heal import self_heal
from agent.validator import run_validation
from agent.budget import LLMBudget

console = Console()


# ----------------------------
# Utilities
# ----------------------------

def clear_workspace():
    """Remove prior generated artifacts so files from an old project do not linger."""
    import shutil

    if not WORKSPACE_DIR.exists():
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        return

    for path in WORKSPACE_DIR.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def write_files(files: dict):
    """
    Replace workspace contents with the generated file set.
    """
    clear_workspace()

    for filename, content in files.items():
        if "/" in filename or "\\" in filename or filename.strip() != filename:
            raise RuntimeError(f"Invalid filename (flat layout only): {filename!r}")

        path = WORKSPACE_DIR / filename
        path.write_text(content)
        console.print(f"[green]✓ wrote[/green] {filename}")


def validate_result_structure(result: dict, phase: str):
    """
    Ensure LLM output has the expected structure.
    """
    if not isinstance(result, dict):
        raise RuntimeError(f"{phase}: result is not a dict")

    if "files" not in result:
        raise RuntimeError(f"{phase}: missing top-level key 'files'")

    if not isinstance(result["files"], dict):
        raise RuntimeError(f"{phase}: 'files' must be a dict")

    if not result["files"]:
        raise RuntimeError(f"{phase}: 'files' must not be empty")


# ----------------------------
# Main Orchestration
# ----------------------------

def main():
    if len(sys.argv) < 2:
        console.print(
            "[red]Error:[/red] Please provide a command.\n"
            "Example:\n"
            "  python cli.py \"Build a CLI that converts temperatures\"\n"
            "  python cli.py \"Create a minimal FastAPI health-check API\""
        )
        sys.exit(1)

    goal = sys.argv[1]
    normalized = normalize_command(goal)
    budget = LLMBudget(MAX_LLM_CALLS)

    console.rule("[bold blue]AI Cursor Agent")
    console.print(f"[bold]Goal:[/bold] {goal}")
    console.print(f"[dim]Normalized:[/dim] {normalized}")
    console.print(f"[dim]LLM budget:[/dim] {budget.remaining}")

    # ----------------------------
    # Cache lookup
    # ----------------------------
    console.rule("[bold cyan]Cache Lookup")

    cached = load_cached(normalized)
    if cached:
        console.print("[green]✓ Cache hit — using cached result[/green]")
        result = eval(cached)  # trusted internal cache
        write_files(result["files"])
        console.print("[bold green]Done (no LLM calls used)[/bold green]")
        return

    console.print("[yellow]Cache miss — generating project[/yellow]")

    # ----------------------------
    # Generation Phase (LLM call #1)
    # ----------------------------
    try:
        console.rule("[bold yellow]LLM Generation")
        console.print(f"Remaining LLM budget: {budget.remaining}")

        result = generate_project(goal, budget)
        validate_result_structure(result, "Generation")

        console.rule("[bold green]Writing Generated Files")
        write_files(result["files"])

    except Exception as e:
        console.print(f"[bold red]Generation failed:[/bold red] {e}")
        return

    # ----------------------------
    # Validation Phase
    # ----------------------------
    console.rule("[bold magenta]Validation (pytest)")
    ok, err = run_validation()

    if ok:
        console.print("[bold green]✓ Validation passed[/bold green]")
        save_cached(normalized, str(result))
        save_last_good(normalized, str(result))
        console.print("[green]✓ Cached result and saved as last-known-good[/green]")
        return

    console.rule("[bold red]Validation Failed")
    console.print(err)

    # ----------------------------
    # Self-Heal Phase (LLM call #2)
    # ----------------------------
    console.rule("[bold yellow]Self-Heal Attempt")
    console.print(f"Remaining LLM budget: {budget.remaining}")

    try:
        healed = self_heal(goal, err, budget)
        validate_result_structure(healed, "Self-heal")

        console.rule("[bold green]Writing Healed Files")
        write_files(healed["files"])

        console.rule("[bold magenta]Re-Validation (pytest)")
        ok, err = run_validation()

        if ok:
            console.print("[bold green]✓ Self-heal successful[/bold green]")
            save_cached(normalized, str(healed))
            save_last_good(normalized, str(healed))
            console.print("[green]✓ Cached healed result[/green]")
            return

        console.print("[bold red]Self-heal validation failed[/bold red]")
        console.print(err)

        raise RuntimeError("Self-heal did not fix the project")

    except Exception as e:
        console.print(f"[bold red]{e}[/bold red]")

    # ----------------------------
    # Fallback: Last Known Good
    # ----------------------------
    console.rule("[bold yellow]Fallback")

    fallback = load_last_good(normalized)
    if fallback:
        console.print("[yellow]Restoring last-known-good output[/yellow]")
        result = eval(fallback)
        write_files(result["files"])
        console.print("[green]✓ Restored last-known-good project[/green]")
    else:
        console.print("[red]No last-known-good output available[/red]")


if __name__ == "__main__":
    main()
