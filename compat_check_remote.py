# -*- coding: utf-8 -*-
"""
🧠 StudioCore Remote Compatibility Check
Проверяет работу ядра, развернутого на HuggingFace Space.
Подключается к /api/predict и выводит результаты проверки.

Author: Bauer Synesthetic Studio
"""

import requests
import json
from datetime import datetime

# === URL твоего API ===
API_URL = "https://sbauer8-studiocore.hf.space/api/predict"

# === Тестовый текст (стресс-тест ядра) ===
TEST_TEXT = """Вся моя жизнь — как быль или небыль,
Вся моя жизнь — по краю скользить.
Но я молю открыть в сердце двери,
Я так хочу твоей женщиной быть…
"""

def run_check():
    print("🧩 Проверка связи с API:", API_URL)
    try:
        # Важно: используем POST, не GET
        response = requests.post(API_URL, json={"text": TEST_TEXT}, timeout=60)
    except Exception as e:
        print("❌ Ошибка при подключении:", e)
        return

    if response.status_code != 200:
        print(f"❌ Ошибка API ({response.status_code}):", response.text)
        return

    try:
        data = response.json()
    except Exception:
        print("⚠️ Не удалось декодировать JSON. Ответ:")
        print(response.text)
        return

    print("\n=== 🧠 ОТЧЁТ О СОВМЕСТИМОСТИ ===")
    summary = data.get("summary", "")
    annotated_text = data.get("annotated_text", "")
    full_prompt = data.get("prompt_full", "")
    suno_prompt = data.get("prompt_suno", "")

    print("📊 Summary:", "OK" if "Жанр" in summary or "Genre" in summary else "⚠️ отсутствует")
    print("🎙️ Annotated text:", "OK" if "[" in annotated_text else "⚠️ не найден")
    print("🎧 Full prompt:", "OK" if len(full_prompt) > 50 else "⚠️ короткий")
    print("🎼 Suno prompt:", "OK" if len(suno_prompt) > 50 else "⚠️ короткий")

    has_tlp = any(tag in summary for tag in ["Truth", "Love", "Pain", "Conscious Frequency"])
    has_tonesync = "ToneSync" in suno_prompt
    print("🩵 TLP:", "✅ найден" if has_tlp else "⚠️ отсутствует")
    print("🎨 ToneSync:", "✅ найден" if has_tonesync else "⚠️ отсутствует")

    if all([has_tlp, has_tonesync, "[" in annotated_text]):
        status = "✅ Ядро StudioCore v5 работает корректно."
    else:
        status = "⚠️ Обнаружены несоответствия, требуется патч или пересборка."

    print("\n" + status)

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "summary": summary,
        "has_tlp": has_tlp,
        "has_tonesync": has_tonesync,
        "annotated_text_preview": "\n".join(annotated_text.splitlines()[:10]),
    }

    with open("remote_compatibility_full_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n📁 Отчёт сохранён в remote_compatibility_full_report.json")

if __name__ == "__main__":
    run_check()
