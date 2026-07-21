import os
import sys
import subprocess
from pathlib import Path

def run_validation(target_dir: Path):
    """
    Runs pytest inside a specific, isolated workspace directory.
    """
    test_files = sorted(target_dir.glob("test_*.py"))
    if not test_files:
        return False, (
            "No test_*.py files found in workspace. "
            "The project must include at least one pytest file "
            "(e.g. test_web.py) that validates the build."
        )

    # Ensure Python prioritizes imports from target_dir over root directory
    env = os.environ.copy()
    env["PYTHONPATH"] = str(target_dir.resolve()) + os.pathsep + env.get("PYTHONPATH", "")

    # Run pytest using the current Python environment's executable
    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=target_dir,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return True, ""

    output = (result.stdout + result.stderr).strip()
    return False, output or "pytest failed with no output"