from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, ClassVar, Dict, Optional


def _to_optional(raw: Optional[str]) -> Optional[str]:
    """Normalize blanks and N/A markers to None."""
    if raw is None:
        return None
    value = raw.strip()
    if not value or value.upper() == "N/A":
        return None
    return value


@dataclass(slots=True)
class MatchProfile:
    """Structured representation of a single player match row."""

    csv_field_to_attr: ClassVar[Dict[str, str]] = {
        "MatchOrdinal": "match_ordinal",
        "Number": "match_number",
        "Date": "date",
        "Season": "season",
        "Competition": "competition",
        "Round": "round",
        "Home/Away": "home_or_away",
        "Home Team": "home_team",
        "Home Score": "home_score",
        "Away Team": "away_team",
        "Away Score": "away_score",
        "Goals": "goals",
        "Assists": "assists",
        "Minutes Played": "minutes_played",
        "Match Rating": "match_rating",
        "Shots": "shots",
        "Shots on Target": "shots_on_target",
        "Free Kick Attempts": "free_kick_attempts",
        "Successful Dribbles": "successful_dribbles",
        "Key Passes": "key_passes",
        "Big Chances Created": "big_chances_created",
        "Accurate Throughballs": "accurate_throughballs",
        "Aerial Duels Won": "aerial_duels_won",
        "xG": "xg",
        "xA": "xa",
        "MOTM": "motm",
    }

    int_fields: ClassVar[set[str]] = {
        "MatchOrdinal",
        "Number",
        "Home Score",
        "Away Score",
        "Goals",
        "Assists",
        "Minutes Played",
        "Shots",
        "Shots on Target",
        "Free Kick Attempts",
        "Successful Dribbles",
        "Key Passes",
        "Big Chances Created",
        "Accurate Throughballs",
        "Aerial Duels Won",
    }

    float_fields: ClassVar[set[str]] = {
        "Match Rating",
        "xG",
        "xA",
    }

    date_format: ClassVar[str] = "%d/%m/%Y"

    match_ordinal: int
    match_number: int
    date: date
    season: Optional[str]
    competition: Optional[str]
    round: Optional[str]
    home_or_away: Optional[str]
    home_team: Optional[str]
    home_score: Optional[int]
    away_team: Optional[str]
    away_score: Optional[int]
    goals: Optional[int]
    assists: Optional[int]
    minutes_played: Optional[int]
    match_rating: Optional[float]
    shots: Optional[int]
    shots_on_target: Optional[int]
    free_kick_attempts: Optional[int]
    successful_dribbles: Optional[int]
    key_passes: Optional[int]
    big_chances_created: Optional[int]
    accurate_throughballs: Optional[int]
    aerial_duels_won: Optional[int]
    xg: Optional[float]
    xa: Optional[float]
    motm: Optional[str]

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "MatchProfile":
        normalized: Dict[str, Any] = {}
        # Support either blank or already-normalized field name for ordinal.
        ordinal_key = "MatchOrdinal"
        if "" in row:
            row = dict(row)
            row[ordinal_key] = row.pop("", None)

        for csv_field, attr in cls.csv_field_to_attr.items():
            value = _to_optional(row.get(csv_field))

            if csv_field == "Date" and value is not None:
                parsed = datetime.strptime(value, cls.date_format).date()
                normalized[attr] = parsed
                continue

            if value is None:
                normalized[attr] = None
                continue

            if csv_field in cls.int_fields:
                normalized[attr] = int(float(value))
            elif csv_field in cls.float_fields:
                normalized[attr] = float(value)
            else:
                normalized[attr] = value

        # Mandatory ints default to zero if missing to avoid runtime errors later.
        if normalized["match_ordinal"] is None:
            raise ValueError("Match ordinal is required for every row.")
        if normalized["match_number"] is None:
            raise ValueError("Match number is required for every row.")

        return cls(**normalized)

    def stat_value(self, attr_name: str) -> Optional[float]:
        if not hasattr(self, attr_name):
            raise AttributeError(f"Unknown stat '{attr_name}' on MatchProfile")
        value = getattr(self, attr_name)
        return value
