from __future__ import annotations

import csv
import io
import tempfile
import textwrap
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from player_match_history import PlayerMatchHistory
from player_match_profile import MatchProfile


CSV_HEADER = ",Number,Date,Season,Competition,Round,Home/Away,Home Team,Home Score,Away Team,Away Score,Goals,Assists,Minutes Played,Match Rating,Shots,Shots on Target,Free Kick Attempts,Successful Dribbles,Key Passes,Big Chances Created,Accurate Throughballs,Aerial Duels Won,xG,xA,MOTM"

CSV_BODY = textwrap.dedent(
    """
    0,2000,01/01/2024,23/24,MLS,,H,Inter Miami,2,LAFC,1,1,,90,8.5,5,3,1,2,3,0,1,0,0.75,0.21,Yes
    1,1999,05/01/2024,23/24,MLS,,A,LA Galaxy,1,Inter Miami,2,2,1,88,8.0,4,2,0,3,1,0,0,1,0.65,0.18,No
    2,1998,10/01/2024,23/24,MLS,,H,Inter Miami,3,Orlando,0,0,0,30,6.5,2,1,0,1,0,0,0,0,0.1,0.05,No
    """
).strip()


class PlayerMatchHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write_csv(self, name: str = "sample.csv", body: str = CSV_BODY) -> Path:
        path = self.tmp_path / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(CSV_HEADER + "\n")
            handle.write(body + "\n")
        return path

    def test_match_profile_parsing(self) -> None:
        csv_content = CSV_HEADER + "\n" + CSV_BODY.splitlines()[0]
        reader = csv.DictReader(io.StringIO(csv_content))
        row = next(reader)
        match = MatchProfile.from_row(row)
        self.assertEqual(match.match_ordinal, 0)
        self.assertEqual(match.goals, 1)
        self.assertIsNone(match.assists)
        self.assertEqual(match.home_team, "Inter Miami")
        self.assertAlmostEqual(match.match_rating or 0, 8.5)

    def test_history_loading_and_name_inference(self) -> None:
        csv_path = self._write_csv("lionel_messi_matches.csv")
        history = PlayerMatchHistory.from_csv(csv_path)
        self.assertEqual(history.player_name, "Lionel Messi Matches")
        self.assertEqual(len(history.matches), 3)
        self.assertEqual(history.matches[0].match_ordinal, 0)

    def test_max_stat_over_span(self) -> None:
        csv_path = self._write_csv()
        history = PlayerMatchHistory.from_csv(csv_path, player_name="Tester")
        summary = history.max_stat_over_span("goals", 2)
        self.assertAlmostEqual(summary.total, 3.0)
        self.assertEqual(len(summary.windows), 1)
        window = summary.windows[0]
        self.assertEqual(window.match_span, 2)
        self.assertEqual(window.start_match.match_ordinal, 0)
        self.assertEqual(window.end_match.match_ordinal, 1)

    def test_max_stat_raises_for_large_span(self) -> None:
        csv_path = self._write_csv()
        history = PlayerMatchHistory.from_csv(csv_path)
        with self.assertRaises(ValueError):
            history.max_stat_over_span("goals", 10)

    def test_duplicate_windows(self) -> None:
        body = textwrap.dedent(
            """
            0,2000,01/01/2024,23/24,MLS,,H,Inter Miami,2,LAFC,1,2,,90,8.5,5,3,1,2,3,0,1,0,0.75,0.21,Yes
            1,1999,02/01/2024,23/24,MLS,,H,Inter Miami,1,Team B,0,1,,90,7.0,2,1,0,1,1,0,0,0,0.5,0.1,No
            2,1998,03/01/2024,23/24,MLS,,H,Inter Miami,1,Team C,0,1,,90,7.0,2,1,0,1,1,0,0,0,0.5,0.1,No
            3,1997,04/01/2024,23/24,MLS,,H,Inter Miami,2,Team D,1,2,,90,7.0,2,1,0,1,1,0,0,0,0.5,0.1,No
            """
        ).strip()
        csv_path = self._write_csv("dup.csv", body=body)
        history = PlayerMatchHistory.from_csv(csv_path)
        summary = history.max_stat_over_span("goals", 2)
        self.assertAlmostEqual(summary.total, 3.0)
        self.assertEqual(len(summary.windows), 2)
        ordinals = [[m.match_ordinal for m in window.matches] for window in summary.windows]
        self.assertIn([0, 1], ordinals)
        self.assertIn([2, 3], ordinals)

    def test_n_goal_in_m_matches_counts(self) -> None:
        csv_path = self._write_csv()
        history = PlayerMatchHistory.from_csv(csv_path)
        summary = history.n_goal_in_m_matches(2, 2)
        self.assertEqual(summary.count, 2)
        self.assertEqual(summary.span, 2)
        self.assertEqual(summary.threshold, 2)
        ordinals = [[m.match_ordinal for m in window.matches] for window in summary.windows]
        self.assertIn([0, 1], ordinals)
        self.assertIn([1, 2], ordinals)

    def test_n_goal_in_m_matches_none(self) -> None:
        csv_path = self._write_csv()
        history = PlayerMatchHistory.from_csv(csv_path)
        summary = history.n_goal_in_m_matches(10, 2)
        self.assertEqual(summary.count, 0)


if __name__ == "__main__":
    unittest.main()
