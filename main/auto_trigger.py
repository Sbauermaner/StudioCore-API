# Auto-trigger for full diagnostics — created 2025-11-21T22:04:15.340308 UTC
import subprocess
import sys
print(">>> AutoTrigger: launching full diagnostics...")
subprocess.run(["bash", "../run_full_diag.sh"], check=True)
print(">>> AutoTrigger complete")
