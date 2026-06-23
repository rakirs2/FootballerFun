from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from player_match_profile import MatchProfile


@dataclass(slots=True)
class StatWindow:
    matches: List[MatchProfile]

    @property
    def match_span(self) -> int:
        return len(self.matches)

    @property
    def start_match(self) -> MatchProfile:
        return self.matches[0]

    @property
    def end_match(self) -> MatchProfile:
        return self.matches[-1]

    @property
    def start_date(self):
        return self.start_match.date

    @property
    def end_date(self):
        return self.end_match.date


@dataclass(slots=True)
class StatWindowSummary:
    stat_name: str
    total: float
    windows: List[StatWindow]


@dataclass(slots=True)
class StatThresholdSummary:
    stat_name: str
    span: int
    threshold: float
    windows: List[StatWindow]

    @property
    def count(self) -> int:
        return len(self.windows)


@dataclass(slots=True)
class PlayerMatchHistory:
    player_name: str
    matches: List[MatchProfile]

    @classmethod
    def from_csv(cls, csv_path: str | Path, player_name: Optional[str] = None) -> "PlayerMatchHistory":
        path = Path(csv_path)
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        matches = [MatchProfile.from_row(row) for row in rows]
        matches.sort(key=lambda m: (m.date, m.match_ordinal))
        name = player_name or path.stem.replace("_", " ").title()
        return cls(player_name=name, matches=matches)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.matches)

    def max_stat_over_span(self, stat_name: str, span: int) -> StatWindowSummary:
        if span <= 0:
            raise ValueError("Span must be a positive integer.")
        if span > len(self.matches):
            raise ValueError("Span cannot exceed total number of matches.")

        attr = self._resolve_stat_name(stat_name)
        values = self._stat_numeric_series(attr, display_name=stat_name)

        current_total = sum(values[:span])
        best_total = current_total
        best_starts = [0]

        for idx in range(span, len(values)):
            current_total += values[idx] - values[idx - span]
            if current_total > best_total:
                best_total = current_total
                best_starts = [idx - span + 1]
            elif current_total == best_total:
                best_starts.append(idx - span + 1)

        windows = [
            StatWindow(matches=list(self.matches[start : start + span]))
            for start in best_starts
        ]
        return StatWindowSummary(stat_name=attr, total=best_total, windows=windows)

    def n_goal_in_m_matches(
        self,
        goals: float,
        span: int,
        stat_name: str = "goals",
    ) -> StatThresholdSummary:
        if span <= 0:
            raise ValueError("Span must be a positive integer.")
        if span > len(self.matches):
            raise ValueError("Span cannot exceed total number of matches.")
        if goals < 0:
            raise ValueError("Goal threshold cannot be negative.")

        attr = self._resolve_stat_name(stat_name)
        values = self._stat_numeric_series(attr, display_name=stat_name)

        windows: List[StatWindow] = []
        total = sum(values[:span])
        if total >= goals:
            windows.append(StatWindow(matches=list(self.matches[:span])))

        for idx in range(span, len(values)):
            total += values[idx] - values[idx - span]
            if total >= goals:
                start = idx - span + 1
                windows.append(StatWindow(matches=list(self.matches[start : start + span])))

        return StatThresholdSummary(
            stat_name=attr,
            span=span,
            threshold=goals,
            windows=windows,
        )

    def _resolve_stat_name(self, stat_name: str) -> str:
        normalized = stat_name.strip().lower().replace(" ", "_")
        for attr in MatchProfile.__dataclass_fields__.keys():
            if attr.lower() == normalized:
                return attr
        raise AttributeError(f"Unknown stat '{stat_name}'.")

    def _stat_numeric_series(self, attr: str, display_name: str) -> List[float]:
        values: List[float] = []
        for match in self.matches:
            value = match.stat_value(attr)
            if value is None:
                values.append(0.0)
            elif isinstance(value, (int, float)):
                values.append(float(value))
            else:
                raise TypeError(
                    f"Stat '{display_name}' must be numeric; got {type(value).__name__}."
                )
        return values
