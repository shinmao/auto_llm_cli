#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

ROOT = Path.home()
CRATE_LIST = ["crate-ver"] # List[str]

# Operational settings
MAX_RETRY = 2                 # retries per crate if status.json not produced
TIMEOUT_SECONDS = 20 * 60     # per attempt timeout (20 minutes)
SLEEP_BETWEEN_RETRY = 3       # seconds

def build_prompt(crate: str) -> str:
    return f"""ROLE: prompt...
"""

def run_codex_exec(prompt: str, cwd: Path, timeout_s: int) -> Tuple[int, str, str]:
    """
    Runs: codex exec "<prompt>"
    Returns: (returncode, stdout, stderr)
    """
    # We run in ROOT so relative paths / ~ expansion in the model instructions stay consistent.
    # codex itself doesn't need cwd, but keeping it stable helps reproducibility.
    proc = subprocess.run(
      ["codex", "exec", "--skip-git-repo-check"],
      cwd=str(cwd),
      input=prompt,
      capture_output=True,
      text=True,
      timeout=timeout_s,
  )

    return proc.returncode, proc.stdout, proc.stderr

def main() -> int:
    crates = read_crate_list(CRATE_LIST)
    if not crates:
        print(f"[FATAL] No crates found in {CRATE_LIST}", file=sys.stderr)
        return 2

    for crate in crates:
        prompt = build_prompt(crate)

        success = False
        for attempt in range(1, MAX_RETRY + 1):
            try:
                rc, out, err = run_codex_exec(prompt, cwd=ROOT, timeout_s=TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                rc, out, err = 124, "", f"Timeout after {TIMEOUT_SECONDS}s"
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

