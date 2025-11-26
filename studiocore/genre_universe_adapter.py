# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .genre_universe import GenreUniverse

logger = logging.getLogger(__name__)


@dataclass
class UniverseResolution:
    macro_genre: str
    subgenre: str
    tags: List[str]
    source: str  # "universe_v2" или "fallback_table"


class GenreUniverseAdapter:
    """
    Простая прослойка между DynamicGenreRouter и GenreUniverse v2.

    Задачи:
    - принять macro_genre (rock_metal / hip_hop / jazz / edm / orchestral / chanson / gothic / folk / pop)
    - попытаться найти подходящий subgenre / universe tags в GenreUniverse
    - если не удалось — вернуть аккуратный fallback без ошибок
    - НЕ хранить состояния, НЕ кешировать; всё статично и детерминировано.
    """

    def __init__(self) -> None:
        self.universe = GenreUniverse()

        # Fallback-таблица — безопасные поджанры на случай, если в реестре нет записи.
        # Codex: НЕ удаляй, можно дополнять.
        self._fallback_map: Dict[str, Tuple[str, List[str]]] = {
            "rock_metal": ("alternative_rock", ["rock", "guitar", "band"]),
            "hip_hop": ("conscious_hip_hop", ["rap", "spoken_word", "beats"]),
            "jazz": ("modern_jazz", ["jazz", "swing", "improv"]),
            "edm": ("cinematic_edm", ["edm", "electronic", "club"]),
            "orchestral": ("cinematic_orchestral", ["orchestral", "score", "strings"]),
            "chanson": ("urban_chanson", ["chanson", "storytelling"]),
            "gothic": ("gothic_rock", ["gothic", "dark", "atmospheric"]),
            "folk": ("neo_folk", ["folk", "acoustic", "story"]),
            "pop": ("modern_pop", ["pop", "hook", "mainstream"]),
        }

    def resolve(
        self,
        macro_genre: str,
        result: Dict[str, Any],
    ) -> UniverseResolution:
        """
        Пытается сопоставить macro_genre с GenreUniverse.

        Приоритет:
        1) Если GenreUniverse уже знает про этот macro_genre — берём оттуда.
        2) Иначе берём fallback из таблицы.
        3) Никогда не кидаем исключения наружу — максимум даём простейший
           subgenre == macro_genre, пустые tags.
        """
        macro = (macro_genre or "unknown").strip()
        if not macro:
            macro = "unknown"

        try:
            if hasattr(self.universe, "resolve_music"):
                resolved = self.universe.resolve_music(macro)  # type: ignore[attr-defined]
                if isinstance(resolved, dict):
                    sub = str(resolved.get("id") or resolved.get("name") or macro)
                    tags = list(resolved.get("tags") or [])
                    if tags:
                        return UniverseResolution(
                            macro_genre=macro,
                            subgenre=sub,
                            tags=tags,
                            source="universe_v2",
                        )
        except (TypeError, ValueError, KeyError, AttributeError) as e:
            # Логируем ошибку вместо молчаливого игнорирования
            # Продолжаем выполнение с fallback
            logger.debug(f"Ошибка при разрешении жанра из universe: {e}")

        if macro in self._fallback_map:
            subgenre, tags = self._fallback_map[macro]
            return UniverseResolution(
                macro_genre=macro,
                subgenre=subgenre,
                tags=list(tags),
                source="fallback_table",
            )

        return UniverseResolution(
            macro_genre=macro,
            subgenre=macro,
            tags=[],
            source="fallback_minimal",
        )

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
