"""
Full workflow diagnostics utility.

Validates GitHub workflow files for YAML syntax, checks referenced files
exist, and ensures required scripts are executable. Mirrors the manual
checks performed in CI so issues can be caught locally.
"""

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"

errors: list[str] = []
info: list[str] = []


def add(msg: str) -> None:
    """Record an error message."""

    errors.append(msg)


# 1. Validate YAML syntax for all workflows
for wf in WF_DIR.glob("*.yml"):
    try:
        txt = wf.read_text(encoding="utf-8")
        yaml.safe_load(txt)
        info.append(f"[OK] YAML syntax valid → {wf.name}")
    except Exception as exc:  # pragma: no cover - diagnostic output
        add(f"[YAML ERROR] {wf.name}: {exc}")

# 2. Verify referenced files in run steps exist
for wf in WF_DIR.glob("*.yml"):
    txt = wf.read_text(encoding="utf-8")
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("run:"):
            cmd = line.replace("run:", "").strip()

            if "run_full_diag.sh" in cmd:
                if not (ROOT / "run_full_diag.sh").exists():
                    add(f"[MISSING FILE] run_full_diag.sh not found (workflow: {wf.name})")

            if "auto_log_cleaner.py" in cmd:
                if not (ROOT / "main" / "auto_log_cleaner.py").exists():
                    add(f"[MISSING FILE] auto_log_cleaner.py not found (workflow: {wf.name})")

            if "full_system_diagnostics.py" in cmd:
                if not (ROOT / "main" / "full_system_diagnostics.py").exists():
                    add(f"[MISSING FILE] full_system_diagnostics.py not found (workflow: {wf.name})")

# 3. Ensure run_full_diag.sh is executable
run_full_diag = ROOT / "run_full_diag.sh"
if run_full_diag.exists():
    mode = run_full_diag.stat().st_mode
    if not (mode & 0o100):
        add("[PERMISSION ERROR] run_full_diag.sh is not executable (chmod +x missing)")
else:
    add("[FILE NOT FOUND] run_full_diag.sh missing")

# 4. Confirm required main/*.py files exist
MAIN = ROOT / "main"
for filename in ["full_system_diagnostics.py", "auto_trigger.py", "auto_log_cleaner.py"]:
    if not (MAIN / filename).exists():
        add(f"[MISSING FILE] main/{filename} does not exist")

print("============== WORKFLOW CHECK ==============")
print("\n".join(info))
print("-------------------------------------------")
if errors:
    print("❌ ERRORS FOUND:")
    print("\n".join(errors))
else:
    print("✔ No workflow errors detected")
