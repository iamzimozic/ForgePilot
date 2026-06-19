import re

def normalize_command(cmd: str) -> str:
    cmd = cmd.lower().strip()
    cmd = re.sub(r"\s+", " ", cmd)
    return cmd
