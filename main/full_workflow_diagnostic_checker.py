# === FULL WORKFLOW DIAGNOSTIC CHECKER ===
# Проверяет все .github/workflows/*.yml на ошибки,
# сообщает какой workflow ломает pipeline, и в какой строке ошибка.

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"

errors = []

print(">>> Scanning workflows...\n")

for wf in WF_DIR.glob("*.yml"):
    print("Checking:", wf.name)

    text = wf.read_text(encoding="utf-8")

    # 1 — YAML syntax
    try:
        data = yaml.safe_load(text)
    except Exception as e:
        errors.append((wf.name, "YAML SYNTAX ERROR", str(e)))
        continue

    # 2 — job definitions
    if "jobs" not in data:
        errors.append((wf.name, "NO JOBS BLOCK", "Missing 'jobs:' root key"))
        continue

    # 3 — check job steps correctness
    for job_name, job in data["jobs"].items():

        # missing 'steps'
        if "steps" not in job:
            errors.append((wf.name, job_name, "Missing 'steps:'"))
            continue

        for step in job["steps"]:
            if "run" in step:
                cmd = step["run"].strip()

                # check correct path to run_full_diag.sh
                if "run_full_diag.sh" in cmd:
                    script_path = ROOT / "run_full_diag.sh"
                    if not script_path.exists():
                        errors.append((wf.name, job_name, f"Script not found: {script_path}"))

                # check reference to auto_log_cleaner.py
                if "auto_log_cleaner.py" in cmd:
                    cleaner = ROOT / "main" / "auto_log_cleaner.py"
                    if not cleaner.exists():
                        errors.append((wf.name, job_name, "auto_log_cleaner.py missing"))

    print("OK:", wf.name, "\n")

print("\n=== RESULTS ===")
if not errors:
    print("All workflows are valid — no structural errors.")
else:
    print("FOUND ERRORS:\n")
    for e in errors:
        print("Workflow:", e[0])
        print("Location:", e[1])
        print("Error:", e[2])
        print("-" * 40)
