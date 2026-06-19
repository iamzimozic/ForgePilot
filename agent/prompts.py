"""Shared LLM instructions for project generation and self-heal."""

COMMON_RULES = """
You are building a small, self-contained project from the user's goal.

SCOPE:
- Keep it small: a few files in one directory.
- Match the goal (CLI, API, library, static webpage, etc.).
- Do not default to CRUD, FastAPI, or SQL unless the goal requires it.

LAYOUT (DO NOT VIOLATE):
- All project files live in ONE directory (no packages, no src/ tree).
- Python modules: flat imports only (no `from .` imports).
- Validation runs `pytest` from the project root — you MUST include Python tests.

TESTS (MANDATORY — WILL BE REJECTED IF MISSING):
- Include at least one file named `test_<something>.py` (e.g. `test_app.py`, `test_web.py`).
- Every project type needs this, including HTML/CSS/JS webpages.
- Tests must pass with: `pytest` (no extra setup).

WEB / HTML / UI GOALS:
- You may include `index.html`, `.css`, `.js` as needed.
- You MUST still include `test_*.py`. Example approaches:
  - Read `index.html` with pathlib and assert calculator elements, buttons, and script hooks exist.
  - Serve static files with a tiny FastAPI/Starlette app and use `TestClient` in tests.
  - Test pure JS logic by importing a small Python shim or checking embedded markup.
- Do NOT return only .html/.css/.js without any `test_*.py` file.

OTHER PROJECT TYPES:
- CLI: `test_cli.py` invoking the CLI via subprocess or direct imports.
- API: `test_main.py` with `TestClient`.
- Library: `test_<module>.py` importing and asserting behavior.

DEPENDENCIES (OPTIONAL):
- If third-party packages are needed, include `requirements.txt` in `files`.

OUTPUT FORMAT (DO NOT VIOLATE):
- Return ONLY valid JSON (must parse with json.loads)
- No markdown fences, no explanations
- File contents are JSON strings: use \\n for newlines, never literal line breaks inside quotes
- Escape quotes in code as \\" and backslashes as \\\\
- JSON structure:

{
  "files": {
    "<filename>": "<single-line string with \\n for newlines>",
    ...
  }
}
"""

GENERATION_PROMPT = COMMON_RULES + """
Generate the complete project that satisfies the user's goal.
Include every file needed to run, open, and test the project.
Double-check: at least one key in `files` must be a `test_*.py` filename.
"""

SELF_HEAL_PROMPT = COMMON_RULES + """
The project failed validation (see error output below).

Fix the project so all tests pass.
If tests were missing, add proper `test_*.py` file(s).
Return the FULL corrected project (all files), not a partial diff.
"""
