# -*- coding: utf-8 -*-
"""
StudioCore Internal Test Runner
Позволяет тестировать ядро отдельно от UI и FastAPI.
"""

import json
import sys
from pathlib import Path
from studiocore import StudioCore, STUDIOCORE_VERSION


def main():
    """
    CLI entrypoint для автономной проверки ядра.
    Можно передавать путь к файлу или сам текст.
    Пример:
      python -m studiocore.app "Мой текст для анализа"
      python -m studiocore.app ./lyrics.txt
    """
    if len(sys.argv) < 2:
        print("Использование: python -m studiocore.app <текстовый_файл_или_строка>")
        sys.exit(1)

    input_data = sys.argv[1]
    if Path(input_data).exists():
        text = Path(input_data).read_text(encoding="utf-8")
    else:
        text = input_data

    core = StudioCore()
    print(f"🧠 StudioCore {STUDIOCORE_VERSION} — автономный анализ\n")

    result = core.analyze(text)
    out_path = "studiocore_result.json"
    Path(out_path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"✅ Анализ завершён. Результат сохранён → {out_path}")


if __name__ == "__main__":
    main()
