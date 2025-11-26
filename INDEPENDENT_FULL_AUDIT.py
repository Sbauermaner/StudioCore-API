#!/usr/bin/env python3
"""
Максимальный независимый аудит проекта StudioCore-API
Проверяет: цвета, иерархию, безопасность, теги, конфликты
"""
import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

class FullAuditor:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.studiocore_dir = self.root_dir / "studiocore"
        self.issues = {
            "color_conflicts": [],
            "missing_colors": [],
            "hierarchy_issues": [],
            "security_issues": [],
            "tag_sticking": [],
            "engine_order": [],
            "missing_formulas": [],
        }
        self.color_sources = {}
        self.engine_calls = []
        
    def audit_all(self):
        """Провести полный аудит"""
        print("="*80)
        print("МАКСИМАЛЬНЫЙ НЕЗАВИСИМЫЙ АУДИТ STUDIOCORE-API")
        print("="*80)
        print()
        
        # 1. Аудит цветов
        print("1. АУДИТ ЦВЕТОВ...")
        self.audit_colors()
        
        # 2. Аудит иерархии
        print("\n2. АУДИТ ИЕРАРХИИ...")
        self.audit_hierarchy()
        
        # 3. Аудит безопасности
        print("\n3. АУДИТ БЕЗОПАСНОСТИ...")
        self.audit_security()
        
        # 4. Аудит тегов
        print("\n4. АУДИТ ТЕГОВ...")
        self.audit_tags()
        
        # 5. Аудит порядка движков
        print("\n5. АУДИТ ПОРЯДКА ДВИЖКОВ...")
        self.audit_engine_order()
        
        # 6. Генерация отчета
        print("\n6. ГЕНЕРАЦИЯ ОТЧЕТА...")
        self.generate_report()
        
    def audit_colors(self):
        """Аудит цветов: конфликты, недостающие, формулы"""
        color_files = [
            "color_engine_adapter.py",
            "genre_colors.py",
            "tone_sync.py",
            "tone.py",
        ]
        
        all_colors = {}
        color_conflicts = defaultdict(list)
        
        for filename in color_files:
            filepath = self.studiocore_dir / filename
            if not filepath.exists():
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Ищем все HEX цвета
            hex_pattern = r'#([0-9A-Fa-f]{6})'
            colors = re.findall(hex_pattern, content)
            
            for color in colors:
                hex_color = f"#{color.upper()}"
                if hex_color not in all_colors:
                    all_colors[hex_color] = []
                all_colors[hex_color].append((filename, content.count(hex_color)))
                
                # Проверяем конфликты (один цвет в разных файлах)
                if len([f for f, _ in all_colors[hex_color] if f != filename]) > 0:
                    color_conflicts[hex_color].append(filename)
        
        # Проверяем формулы цветов
        core_v6 = self.studiocore_dir / "core_v6.py"
        if core_v6.exists():
            with open(core_v6, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем наличие функций blend, gradient и т.д.
            color_functions = ["blend", "gradient", "soften", "warm_shift", "saturate", "darken", "fade"]
            for func in color_functions:
                if func not in content:
                    self.issues["missing_formulas"].append(f"Отсутствует функция {func}() для Color_Formula")
        
        # Сохраняем результаты
        self.color_sources = all_colors
        self.issues["color_conflicts"] = list(color_conflicts.items())
        
        print(f"  Найдено цветов: {len(all_colors)}")
        print(f"  Конфликтов: {len(color_conflicts)}")
        print(f"  Отсутствующих формул: {len(self.issues['missing_formulas'])}")
        
    def audit_hierarchy(self):
        """Аудит иерархии движков и ядер"""
        core_v6 = self.studiocore_dir / "core_v6.py"
        if not core_v6.exists():
            return
            
        with open(core_v6, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Ищем порядок вызова движков в _backend_analyze
        expected_order = [
            "Structure", "Emotion", "TLP", "RDE", "Color", 
            "Vocal", "BPM", "Tonality", "Genre", "Instrumentation",
            "Annotations", "StylePrompt", "Suno", "Output"
        ]
        
        found_order = []
        in_backend_analyze = False
        
        for i, line in enumerate(lines, 1):
            if "def _backend_analyze" in line:
                in_backend_analyze = True
            elif in_backend_analyze and line.strip().startswith("def "):
                in_backend_analyze = False
                
            if in_backend_analyze:
                for step in expected_order:
                    if step.lower() in line.lower() and step not in found_order:
                        found_order.append(step)
                        self.engine_calls.append((i, step, line.strip()[:80]))
        
        # Проверяем порядок
        if found_order != expected_order:
            self.issues["engine_order"].append({
                "expected": expected_order,
                "found": found_order,
                "missing": [s for s in expected_order if s not in found_order],
            })
        
        print(f"  Найдено этапов: {len(found_order)}/{len(expected_order)}")
        print(f"  Отсутствующих: {len(self.issues['engine_order'])}")
        
    def audit_security(self):
        """Аудит безопасности: eval, exec, shell=True, etc."""
        security_patterns = {
            "eval": r'\beval\s*\(',
            "exec": r'\bexec\s*\(',
            "shell=True": r'shell\s*=\s*True',
            "subprocess_shell": r'subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True',
            "pickle": r'pickle\.(load|loads)',
            "yaml_load": r'yaml\.load\s*\(',
        }
        
        for py_file in self.studiocore_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern_name, pattern in security_patterns.items():
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.issues["security_issues"].append({
                            "file": str(py_file.relative_to(self.root_dir)),
                            "line": line_num,
                            "pattern": pattern_name,
                            "code": content.split('\n')[line_num-1].strip()[:100],
                        })
            except Exception as e:
                pass
        
        print(f"  Найдено проблем безопасности: {len(self.issues['security_issues'])}")
        
    def audit_tags(self):
        """Аудит залипания тегов (сохранение тегов между анализами)"""
        core_v6 = self.studiocore_dir / "core_v6.py"
        if not core_v6.exists():
            return
            
        with open(core_v6, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем классы и методы, которые могут хранить состояние
        class_pattern = r'class\s+(\w+).*?:'
        classes = re.findall(class_pattern, content)
        
        # Проверяем наличие reset методов
        for cls in classes:
            if f"def reset" not in content and f"def _reset" not in content:
                # Проверяем, есть ли атрибуты класса, которые могут залипать
                if f"self.{cls.lower()}" in content or f"self._section" in content:
                    self.issues["tag_sticking"].append({
                        "class": cls,
                        "issue": "Возможное залипание тегов (нет reset метода)",
                    })
        
        print(f"  Найдено потенциальных проблем с тегами: {len(self.issues['tag_sticking'])}")
        
    def audit_engine_order(self):
        """Аудит порядка вызова движков"""
        # Уже выполнено в audit_hierarchy, но добавляем детали
        if self.issues["engine_order"]:
            for issue in self.issues["engine_order"]:
                missing = issue.get("missing", [])
                if missing:
                    print(f"  Отсутствуют этапы: {', '.join(missing)}")
        
    def generate_report(self):
        """Генерация полного отчета"""
        report = {
            "summary": {
                "color_conflicts": len(self.issues["color_conflicts"]),
                "missing_colors": len(self.issues["missing_colors"]),
                "hierarchy_issues": len(self.issues["hierarchy_issues"]),
                "security_issues": len(self.issues["security_issues"]),
                "tag_sticking": len(self.issues["tag_sticking"]),
                "engine_order": len(self.issues["engine_order"]),
                "missing_formulas": len(self.issues["missing_formulas"]),
            },
            "details": self.issues,
            "color_sources": {k: len(v) for k, v in self.color_sources.items()},
            "engine_calls": self.engine_calls[:20],  # Первые 20
        }
        
        report_file = self.root_dir / "FULL_AUDIT_REPORT.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Текстовый отчет
        report_txt = self.root_dir / "FULL_AUDIT_REPORT.md"
        with open(report_txt, 'w', encoding='utf-8') as f:
            f.write("# ПОЛНЫЙ АУДИТ ПРОЕКТА STUDIOCORE-API\n\n")
            f.write("## Сводка\n\n")
            f.write(f"- Конфликты цветов: {report['summary']['color_conflicts']}\n")
            f.write(f"- Проблемы безопасности: {report['summary']['security_issues']}\n")
            f.write(f"- Проблемы с тегами: {report['summary']['tag_sticking']}\n")
            f.write(f"- Проблемы порядка: {report['summary']['engine_order']}\n")
            f.write(f"- Отсутствующие формулы: {report['summary']['missing_formulas']}\n")
            f.write("\n## Детали\n\n")
            f.write("См. FULL_AUDIT_REPORT.json для полных деталей.\n")
        
        print(f"  Отчет сохранен: {report_file}")
        print(f"  Текстовый отчет: {report_txt}")

if __name__ == "__main__":
    auditor = FullAuditor(".")
    auditor.audit_all()

