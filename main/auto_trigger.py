# Auto-trigger for full diagnostics
# Runs run_full_diag.sh safely from GitHub Actions and local CI.

import subprocess
from pathlib import Path


def main():
    print(">>> AutoTrigger: launching full diagnostics...")
    script = Path(__file__).resolve().parent.parent / "run_full_diag.sh"
    
    # Task 1.2: Add timeout to prevent infinite hangs
    if not script.exists():
        print(f"❌ ERROR: Script not found at {script}")
        return 1
    
    try:
        subprocess.run(
            ["bash", str(script)],
            check=True,
            timeout=300,  # 5 minutes timeout
        )
        print(">>> AutoTrigger complete")
        return 0
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Script execution timed out after 5 minutes")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Script failed with exit code {e.returncode}")
        return 1
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    main()
