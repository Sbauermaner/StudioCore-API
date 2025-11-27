# StudioCore Self-Healing Engine
# Анализирует lgp.txt и исправляет распространённые типы ошибок.

import os
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LGP = ROOT / "main" / "lgp.txt"


def heal(fix_workflows: bool | None = None):
    if not LGP.exists():
        return "lgp.txt not found"

    txt = LGP.read_text(encoding="utf-8")
    original_txt = txt
    fixes = []

    # Workflow правки по умолчанию отключены; включаются только явным
    # флагом/переменной.
    enable_workflow_fixes = (
        fix_workflows
        if fix_workflows is not None
        else os.getenv("STUDIOCORE_HEAL_WORKFLOWS", "").strip() == "1"
    )

    # 1. Удаление старых тегов, если они случайно появились в коде
    old_tags = [
        "cinematic narrative",
        "majestic major",
        "EMOTION: neutral",
        "female soprano",
        "[91 BPM]",
        "choir_mixed",
    ]
    for tag in old_tags:
        if tag in txt:
            txt = txt.replace(tag, "")
            fixes.append(f"removed stale tag {tag}")

    # 2. Исправление пустых секций (если анализ отдал [] где не должен)
    if "Segmentation: []" in txt:
        txt = txt.replace("Segmentation: []", "Segmentation: [not detected]")
        fixes.append("fixed empty segmentation fallback")

    # 3. Автоисправление неправильного пути в workflows
    if enable_workflow_fixes:
        wf = ROOT / ".github" / "workflows"
        for yml in wf.glob("*.yml"):
            # Task 2.1: Create backup before modifying files
            backup_path = yml.with_suffix(yml.suffix + ".bak")
            try:
                shutil.copy2(yml, backup_path)
            except Exception as e:
                fixes.append(f"WARNING: Could not create backup for {yml.name}: {e}")
                continue
            
            content = yml.read_text(encoding="utf-8")
            new = content.replace(
                "bash ./run_full_diag.sh",
                "bash ${{ github.workspace }}/run_full_diag.sh",
            )
            if new != content:
                # Task 2.1: Validate YAML syntax before saving
                try:
                    yaml.safe_load(new)
                    yml.write_text(new, encoding="utf-8")
                    fixes.append(f"workflow fixed path in {yml.name}")
                except yaml.YAMLError as e:
                    fixes.append(f"ERROR: Invalid YAML after fix in {yml.name}: {e}")
                    # Restore from backup
                    try:
                        shutil.copy2(backup_path, yml)
                    except Exception:
                        pass

        # 4. Исправление конфликтов python3/python
        for yml in wf.glob("*.yml"):
            # Task 2.1: Create backup before modifying files
            backup_path = yml.with_suffix(yml.suffix + ".bak")
            try:
                shutil.copy2(yml, backup_path)
            except Exception as e:
                fixes.append(f"WARNING: Could not create backup for {yml.name}: {e}")
                continue
            
            content = yml.read_text(encoding="utf-8")
            new = content.replace("python main/", "python3 main/")
            if new != content:
                # Task 2.1: Validate YAML syntax before saving
                try:
                    yaml.safe_load(new)
                    yml.write_text(new, encoding="utf-8")
                    fixes.append(f"python3 normalization in {yml.name}")
                except yaml.YAMLError as e:
                    fixes.append(f"ERROR: Invalid YAML after fix in {yml.name}: {e}")
                    # Restore from backup
                    try:
                        shutil.copy2(backup_path, yml)
                    except Exception:
                        pass

    # 5. Удаление сломанных пустых значений diagnostics
    if "Diagnostics: None" in txt:
        txt = txt.replace("Diagnostics: None", "Diagnostics: []")
        fixes.append("normalized empty diagnostics block")

    # Apply fixes to file if any were made
    if txt != original_txt:
        # Task 2.1: Create backup before modifying lgp.txt
        backup_path = LGP.with_suffix(LGP.suffix + ".bak")
        try:
            shutil.copy2(LGP, backup_path)
        except Exception as e:
            fixes.append(f"WARNING: Could not create backup for lgp.txt: {e}")
        
        LGP.write_text(txt, encoding="utf-8")
        # write results into lgp
        with LGP.open("a", encoding="utf-8") as f:
            f.write(f"\n[SELF-HEAL] Applied fixes: {len(fixes)} ({','.join(fixes)})\n")

    return fixes


if __name__ == "__main__":
    out = heal()
    print("Self-Heal Completed:", out)
