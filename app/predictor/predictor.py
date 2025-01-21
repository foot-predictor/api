import logging
from collections import Counter

import numpy as np
import pandas as pd

from models.matchs import MatchResult, MatchSide
from models.teams import Team
from predictor.models import GlobalStatistics, Prediction, TeamStatistics, ThresholdGoal

logger = logging.getLogger(__name__)


class PredictorError(Exception): ...


class Predictor:
    MAX_GOALS = 5
    home_stats: GlobalStatistics
    away_stats: GlobalStatistics

    def __init__(self, home_team: Team, away_team: Team):
        self.home = home_team
        self.away = away_team

        common_competitions = set(home_team._competitions) & set(
            away_team._competitions
        )
        assert common_competitions
        self.common_competitions = list(common_competitions)

    @staticmethod
    def _aggregate_stats(df: pd.DataFrame) -> TeamStatistics:
        return TeamStatistics(
            matches_played=df.shape[0],
            wins=df[df["result"] == MatchResult.WIN.value].shape[0],
            draws=df[df["result"] == MatchResult.DRAW.value].shape[0],
            losses=df[df["result"] == MatchResult.LOSE.value].shape[0],
            goals_for=df["goal_for"].sum(),
            goals_against=df["goal_against"].sum(),
            fouls=df["fouls"].sum(),
            shots=df["shots"].sum(),
            shots_off_goal=df["shots_off_goal"].sum(),
            shots_on_goal=df["shots_on_goal"].sum(),
            possession=(df["possession"].mean() / 100),
            external_xg=df["livescore_xg"].mean(skipna=True),
        )

    @staticmethod
    def _transform_data(matches_df: pd.DataFrame) -> GlobalStatistics:
        home_matches = matches_df[matches_df["side"] == MatchSide.HOME.value]
        away_matches = matches_df[matches_df["side"] == MatchSide.AWAY.value]

        # Aggregate statistics
        home_stats = Predictor._aggregate_stats(home_matches)
        away_stats = Predictor._aggregate_stats(away_matches)

        return GlobalStatistics(home_statistics=home_stats, away_statistics=away_stats)

    def enhance_team_statistics(
        self, home_matches: pd.DataFrame, away_matches: pd.DataFrame
    ):
        logger.info(f"Aggregating team matches statistics for [{self.home.short_name}]")
        self.home_stats = self._transform_data(home_matches)
        logger.info(f"Aggregating team matches statistics for [{self.away.short_name}]")
        self.away_stats = self._transform_data(away_matches)

    def _adjust_xg(self) -> tuple[float, float]:
        home_win_rate = self.home_stats.wins / self.home_stats.matches_played
        away_win_rate = self.away_stats.wins / self.away_stats.matches_played
        advantage = (
            (home_win_rate - away_win_rate) / (home_win_rate + away_win_rate) * 0.5
        )

        home_xg = (
            self.home_stats.xg * 0.2 + self.home_stats.home_statistics.xg * 0.8
        ) * (1 + advantage)

        away_xg = (
            self.away_stats.xg * 0.2 + self.away_stats.away_statistics.xg * 0.8
        ) * (0.9 - advantage)
        return home_xg, away_xg

    def simulate(self, iterations: int = 10000) -> Prediction:
        """Use Monte Carlo simulation with poisson probability calculation"""
        if self.home_stats is None or self.away_stats is None:
            raise PredictorError(
                "Team statistics not aggregated yet, please run enhance_team_statistics"
            )

        home_xg, away_xg = self._adjust_xg()
        logging.info(
            f"Simulating for {self.home.short_name}({home_xg}) vs {self.away.short_name}({away_xg})"
        )
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

        return Prediction(
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
