import numpy as np
import pandas as pd
from scipy.stats import poisson, norm

class SportsPredictor:
    def __init__(self, k_factor=32):
        self.k_factor = k_factor
        self.ratings = {}  # Team ratings: {team_name: elo}
        self.history = []

    def get_rating(self, team):
        return self.ratings.get(team, 1500)

    def calculate_expected(self, rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_ratings(self, winner, loser):
        rating_w = self.get_rating(winner)
        rating_l = self.get_rating(loser)
        
        expected_w = self.calculate_expected(rating_w, rating_l)
        
        self.ratings[winner] = rating_w + self.k_factor * (1 - expected_w)
        self.ratings[loser] = rating_l + self.k_factor * (0 - (1 - expected_w))

    def train_on_history(self, df):
        """
        Trains the Elo model on historical game data.
        """
        for _, row in df.iterrows():
            if row['home_score'] > row['away_score']:
                self.update_ratings(row['home_team'], row['away_team'])
            elif row['away_score'] > row['home_score']:
                self.update_ratings(row['away_team'], row['home_team'])

    def predict_matchup_poisson(self, home_team, away_team, catalysts=None, hfa=50):
        """
        Predicts win probability using a Catalyst-Weighted Poisson model.
        catalysts: Dictionary of team-specific impact factors (e.g. {'Lakers': 0.95})
        """
        r_home = self.get_rating(home_team) + hfa
        r_away = self.get_rating(away_team)
        
        # Base expected goals/runs (Poisson Lambda)
        # Assuming 1500 Elo maps to a baseline like 100 points in NBA, 4 runs in MLB, etc.
        # This is a simplified mapping for simulation purposes.
        avg_score_ref = 100 
        lambda_h = (r_home / r_away) * (avg_score_ref / 10)
        lambda_a = (r_away / r_home) * (avg_score_ref / 10)

        # Apply Catalyst Weights (e.g. Injuries)
        if catalysts:
            lambda_h *= catalysts.get(home_team, 1.0)
            lambda_a *= catalysts.get(away_team, 1.0)

        # Simulate 10k games using Poisson
        sim_h = np.random.poisson(lambda_h, 10000)
        sim_a = np.random.poisson(lambda_a, 10000)
        
        win_h = np.sum(sim_h > sim_a) / 10000
        win_a = np.sum(sim_a > sim_h) / 10000
        draw = np.sum(sim_h == sim_a) / 10000
        
        # Distribute draws for a binary win/loss prediction if required
        total_prob = win_h + win_a
        return win_h / total_prob, win_a / total_prob

    def calculate_brier_score(self, predictions, outcomes):
        """
        Measures the accuracy of probabilistic predictions.
        (Prob - Outcome)^2
        """
        return np.mean((np.array(predictions) - np.array(outcomes))**2)

    def calculate_ev(self, model_prob, decimal_odds):
        return (model_prob * decimal_odds) - 1

    def analyze_bet(self, home_team, away_team, home_odds, away_odds, catalysts=None):
        prob_h, prob_a = self.predict_matchup_poisson(home_team, away_team, catalysts=catalysts)
        
        ev_h = self.calculate_ev(prob_h, home_odds)
        ev_a = self.calculate_ev(prob_a, away_odds)
        
        implied_market_h = 1 / home_odds
        implied_market_a = 1 / away_odds
        
        # Monte Carlo for Confidence Intervals
        sims_h = np.random.binomial(1, prob_h, 10000)
        std_err_h = np.std(sims_h) / np.sqrt(10000)
        ci_h = (prob_h - 1.96 * std_err_h, prob_h + 1.96 * std_err_h)

        return {
            "home": {
                "team": home_team,
                "prob": prob_h,
                "ev": ev_h,
                "market_implied": implied_market_h,
                "edge": prob_h - implied_market_h,
                "confidence_interval": ci_h
            },
            "away": {
                "team": away_team,
                "prob": prob_a,
                "ev": ev_a,
                "market_implied": implied_market_a,
                "edge": prob_a - implied_market_a
            }
        }
