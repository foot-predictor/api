from collections import Counter

import numpy as np
import pandas as pd

from models import MatchPredictions, Team, TeamAllStats, TeamSideStats, ThresholdGoal


class Predictor:
    MAX_GOALS = 5

    def __init__(self, home_team: Team, away_team: Team):
        self.home = home_team
        self.away = away_team
        self.home_stats = None
        self.away_stats = None

    @staticmethod
    def _aggregate_stats(stats: pd.DataFrame, is_home: bool) -> TeamSideStats:
        team = "HOME" if is_home else "AWAY"
        opponent = "AWAY" if is_home else "HOME"

        passes_accuracy_avg = stats[f"{team.lower()}.passes_accurate"].sum(
            skipna=True
        ) / stats[f"{team.lower()}.passes_total"].sum(skipna=True)

        return TeamSideStats(
            gf=stats[f"score.fullTime.{team.lower()}"].sum(skipna=True),
            ga=stats[f"score.fullTime.{opponent.lower()}"].sum(skipna=True),
            mp=stats.shape[0],
            wins=stats[stats["score.winner"] == f"{team}_TEAM"].shape[0],
            draws=stats[stats["score.winner"] == "DRAW"].shape[0],
            loses=stats[stats["score.winner"] == f"{opponent}_TEAM"].shape[0],
            nb_attacks=stats[f"{team.lower()}.attacks"].sum(skipna=True),
            nb_shots_total=stats[f"{team.lower()}.shots_total"].sum(skipna=True),
            nb_shots_on_goal_total=stats[f"{team.lower()}.shots_on_goal"].sum(
                skipna=True
            ),
            possession_avg=stats[f"{team.lower()}.ball_possession"].mean(skipna=True)
            / 100,
            passes_accuracy_avg=passes_accuracy_avg,
        )

    @staticmethod
    def _transform_data(team: Team, matches_df: pd.DataFrame) -> TeamAllStats:
        home_matches = matches_df[matches_df["homeTeam.id"] == team.data_id]
        away_matches = matches_df[matches_df["awayTeam.id"] == team.data_id]

        # Aggregate statistics
        home_stats = Predictor._aggregate_stats(home_matches, is_home=True)
        away_stats = Predictor._aggregate_stats(away_matches, is_home=False)

        return TeamAllStats(
            team=team,
            gf=home_stats.gf + away_stats.gf,
            ga=home_stats.ga + away_stats.ga,
            mp=home_stats.mp + away_stats.mp,
            wins=home_stats.wins + away_stats.wins,
            draws=home_stats.draws + away_stats.draws,
            loses=home_stats.loses + away_stats.loses,
            home=home_stats,
            away=away_stats,
        )

    def enhance_team_statistics(
        self, home_matches: pd.DataFrame, away_matches: pd.DataFrame
    ):
        self.home_stats = self._transform_data(self.home, home_matches)
        self.away_stats = self._transform_data(self.away, away_matches)

    def _adjust_xg(self) -> tuple[float, float]:
        home_win_rate = self.home_stats.wins / self.home_stats.mp
        away_win_rate = self.away_stats.wins / self.away_stats.mp
        advantage = (home_win_rate - away_win_rate) / (home_win_rate + away_win_rate)

        home_xg = (self.home_stats.xg * 0.4 + self.home_stats.home.xg * 0.6) * (
            1 + advantage
        )

        away_xg = (self.away_stats.xg * 0.4 + self.away_stats.away.xg * 0.6) * (
            1 - advantage
        )
        return home_xg, away_xg

    def simulate(self, iterations=10000):
        """Use Monte Carlo simulation with poisson probability calculation"""
        home_xg, away_xg = self._adjust_xg()
        home_win = 0
        draw = 0
        away_win = 0
        btts = 0
        exact_scores = []
        goals = {
            0.5: {
                "global": {"below": 0, "over": 0},
                "home": {"below": 0, "over": 0},
                "away": {"below": 0, "over": 0},
            },
            1.5: {
                "global": {"below": 0, "over": 0},
                "home": {"below": 0, "over": 0},
                "away": {"below": 0, "over": 0},
            },
            2.5: {
                "global": {"below": 0, "over": 0},
                "home": {"below": 0, "over": 0},
                "away": {"below": 0, "over": 0},
            },
            3.5: {
                "global": {"below": 0, "over": 0},
                "home": {"below": 0, "over": 0},
                "away": {"below": 0, "over": 0},
            },
        }
        for _ in range(iterations):
            home_goals = min(np.random.poisson(home_xg), self.MAX_GOALS)
            away_goals = min(np.random.poisson(away_xg), self.MAX_GOALS)

            # Track Wins probability
            if home_goals > away_goals:
                home_win += 1
            elif home_goals == away_goals:
                draw += 1
            else:
                away_win += 1

            # Track goals BTTS probability
            btts += 1 if home_goals > 0 and away_goals > 0 else 0

            for threshold in goals.keys():
                goals[threshold]["global"]["below"] += (
                    1 if home_goals + away_goals < threshold else 0
                )
                goals[threshold]["global"]["over"] += (
                    1 if home_goals + away_goals > threshold else 0
                )
                goals[threshold]["home"]["below"] += 1 if home_goals < threshold else 0
                goals[threshold]["home"]["over"] += 1 if home_goals > threshold else 0
                goals[threshold]["away"]["below"] += 1 if away_goals < threshold else 0
                goals[threshold]["away"]["over"] += 1 if away_goals > threshold else 0

            # Track exact score
            exact_scores.append((home_goals, away_goals))

        return MatchPredictions(
            home_team=self.home_stats,
            away_team=self.away_stats,
            home_win=round((home_win / iterations) * 100),
            draw=round((draw / iterations) * 100),
            away_win=round((away_win / iterations) * 100),
            btts=round((btts / iterations) * 100),
            global_threshold_goals=[
                ThresholdGoal(
                    threshold=threshold,
                    below=round(
                        (goals[threshold]["global"]["below"] / iterations) * 100
                    ),
                    over=round((goals[threshold]["global"]["over"] / iterations) * 100),
                )
                for threshold in goals.keys()
            ],
            home_threshold_goals=[
                ThresholdGoal(
                    threshold=threshold,
                    below=round((goals[threshold]["home"]["below"] / iterations) * 100),
                    over=round((goals[threshold]["home"]["over"] / iterations) * 100),
                )
                for threshold in goals.keys()
            ],
            away_threshold_goals=[
                ThresholdGoal(
                    threshold=threshold,
                    below=round((goals[threshold]["away"]["below"] / iterations) * 100),
                    over=round((goals[threshold]["away"]["over"] / iterations) * 100),
                )
                for threshold in goals.keys()
            ],
            exact_score=[
                {f"{score[0]}-{score[1]}": round((count / iterations) * 100)}
                for score, count in Counter(exact_scores).most_common()[:3]
            ],
        )
