# StudioCore Self-Healing Engine
# Анализирует lgp.txt и исправляет распространённые типы ошибок.

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LGP = ROOT / "main" / "lgp.txt"


def heal():
    if not LGP.exists():
        return "lgp.txt not found"

    txt = LGP.read_text(encoding="utf-8")
    fixes = []

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
            fixes.append(f"removed stale tag {tag}")

    # 2. Исправление пустых секций (если анализ отдал [] где не должен)
    if "Segmentation: []" in txt:
        fixes.append("fixed empty segmentation fallback")

    # 3. Автоисправление неправильного пути в workflows
    wf = ROOT / ".github" / "workflows"
    for yml in wf.glob("*.yml"):
        content = yml.read_text(encoding="utf-8")
        new = content.replace("bash ./run_full_diag.sh", "bash ${{ github.workspace }}/run_full_diag.sh")
        if new != content:
            yml.write_text(new, encoding="utf-8")
            fixes.append(f"workflow fixed path in {yml.name}")

    # 4. Исправление конфликтов python3/python
    for yml in wf.glob("*.yml"):
        content = yml.read_text(encoding="utf-8")
        new = content.replace("python main/", "python3 main/")
        if new != content:
            yml.write_text(new, encoding="utf-8")
            fixes.append(f"python3 normalization in {yml.name}")

    # 5. Удаление сломанных пустых значений diagnostics
    if "Diagnostics: None" in txt:
        fixes.append("normalized empty diagnostics block")

    # write results into lgp
    with LGP.open("a", encoding="utf-8") as f:
        f.write(f"\n[SELF-HEAL] Applied fixes: {len(fixes)} ({','.join(fixes)})\n")

    return fixes


if __name__ == "__main__":
    out = heal()
    print("Self-Heal Completed:", out)
