import subprocess
from config import WORKSPACE_DIR


def run_validation():
    test_files = sorted(WORKSPACE_DIR.glob("test_*.py"))
    if not test_files:
        return False, (
            "No test_*.py files found in workspace. "
            "The project must include at least one pytest file "
            "(e.g. test_web.py) that validates the build."
        )

    result = subprocess.run(
        "pytest",
        cwd=WORKSPACE_DIR,
        shell=True,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return True, ""

    output = (result.stdout + result.stderr).strip()
    return False, output or "pytest failed with no output"
