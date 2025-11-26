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


def _collect_workflow_diagnostics() -> tuple[list[str], list[str]]:
    """Gather workflow validation info and error messages."""

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
    main_dir = ROOT / "main"
    for filename in ["full_system_diagnostics.py", "auto_trigger.py", "auto_log_cleaner.py"]:
        if not (main_dir / filename).exists():
            add(f"[MISSING FILE] main/{filename} does not exist")

    return errors, info


def main() -> int:
    errors, info = _collect_workflow_diagnostics()

    print("============== WORKFLOW CHECK ==============")
    print("\n".join(info))
    print("-------------------------------------------")
    if errors:
        print("❌ ERRORS FOUND:")
        print("\n".join(errors))
        exit_code = 1
    else:
        print("✔ No workflow errors detected")
        exit_code = 0

    # Write results to lgp.txt as expected by run_full_diag.sh
    lgp_path = ROOT / "main" / "lgp.txt"
    from datetime import datetime
    header = "=== StudioCore — FULL SYSTEM DIAGNOSTIC REPORT ==="
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    report = f"\n{header}\n"
    report += f"Timestamp: {timestamp}\n"
    report += "\n".join(info) + "\n"
    if errors:
        report += "\n".join(errors) + "\n"
    report += f"Status: {'FAILED' if errors else 'PASSED'}\n"
    report += "=" * 50 + "\n"
    
    lgp_path.parent.mkdir(parents=True, exist_ok=True)
    with lgp_path.open("a", encoding="utf-8") as f:
        f.write(report)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
