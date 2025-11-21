# Auto-trigger for full diagnostics
# Runs run_full_diag.sh safely from GitHub Actions and local CI.

import subprocess
import sys
from pathlib import Path


def main():
    print(">>> AutoTrigger: launching full diagnostics...")
    script = Path(__file__).resolve().parent.parent / "run_full_diag.sh"
    subprocess.run(["bash", str(script)], check=True)
    print(">>> AutoTrigger complete")


if __name__ == "__main__":
    main()
