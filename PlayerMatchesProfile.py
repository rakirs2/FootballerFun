from __future__ import annotations

import argparse
from pathlib import Path

from player_match_history import PlayerMatchHistory


def main() -> None:
    parser = argparse.ArgumentParser(description="Player match profile analyzer")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="leomessi_matches.csv",
        help="Path to the CSV containing match data",
    )
    parser.add_argument(
        "--player-name",
        dest="player_name",
        help="Override the inferred player name",
    )
    parser.add_argument(
        "--stat",
        dest="stat_name",
        help="Statistic to evaluate for a sliding window (e.g., goals)",
    )
    parser.add_argument(
        "--span",
        type=int,
        default=5,
        help="Number of games in the sliding window",
    )
    parser.add_argument(
        "--threshold-goals",
        dest="threshold_goals",
        type=float,
        help="Minimum goals for the threshold query (default 13)",
    )
    parser.add_argument(
        "--threshold-span",
        dest="threshold_span",
        type=int,
        help="Span length (matches) for the threshold query (default 5)",
    )
    args = parser.parse_args()

    history = PlayerMatchHistory.from_csv(args.csv_path, player_name=args.player_name)
    print(f"Loaded {len(history.matches)} matches for {history.player_name}.")

    first = history.matches[0]
    last = history.matches[-1]
    print(
        "Match range: "
        f"{first.date.isoformat()} ({first.competition}) -> "
        f"{last.date.isoformat()} ({last.competition})"
    )

    if args.stat_name:
        summary = history.max_stat_over_span(args.stat_name, args.span)
        print(
            f"Max {summary.stat_name} over {args.span} games: {summary.total:.2f}"
        )
        for idx, window in enumerate(summary.windows, start=1):
            start = window.start_match
            end = window.end_match
            print(
                f"Window {idx}: {start.date.isoformat()} (Match {start.match_number}) -> "
                f"{end.date.isoformat()} (Match {end.match_number})"
            )
            print("Matches in window:")
            for match in window.matches:
                stat_value = getattr(match, summary.stat_name)
                print(
                    f"  #{match.match_ordinal} {match.date.isoformat()} "
                    f"{match.home_team} vs {match.away_team} | {summary.stat_name}="
                    f"{stat_value}"
                )

    threshold_goals = args.threshold_goals if args.threshold_goals is not None else 13
    threshold_span = args.threshold_span if args.threshold_span is not None else 5
    threshold_summary = history.n_goal_in_m_matches(
        threshold_goals,
        threshold_span,
    )
    print(
        f"Reached ≥{threshold_summary.threshold} {threshold_summary.stat_name} "
        f"across {threshold_summary.span} matches: {threshold_summary.count} times"
    )
    if threshold_summary.count:
        for idx, window in enumerate(threshold_summary.windows, start=1):
            start = window.start_match
            end = window.end_match
            print(
                f"  Occurrence {idx}: {start.date.isoformat()} (Match {start.match_number}) -> "
                f"{end.date.isoformat()} (Match {end.match_number})"
            )
    else:
        print("  No windows met the threshold.")


if __name__ == "__main__":
    main()
