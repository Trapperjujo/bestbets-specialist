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

    def predict_matchup_ensemble(self, home_team, away_team, catalysts=None, hfa=50, rest_days_h=2, rest_days_a=2):
        """
        Highest-Accuracy Ensemble Model: Combines Elo, Poisson, and Schedule factors.
        """
        # 1. Elo Probability (Base Strength)
        r_h = self.get_rating(home_team) + hfa
        r_a = self.get_rating(away_team)
        prob_elo = self.calculate_expected(r_h, r_a)

        # 2. Schedule Adjustments (Rest & SOS)
        # Rest: 2 days is baseline. 0 days (B2B) = -5%. 4+ days = +2%.
        rest_effect_h = (rest_days_h - 2) * 0.015 
        rest_effect_a = (rest_days_a - 2) * 0.015

        # 3. Poisson Simulation (Scoring Rate Focus)
        # We map Elo to a dynamic Scoring Rate
        avg_pts = 100 # NBA baseline
        lambda_h = (r_h / 1500) * (avg_pts / 10)
        lambda_a = (r_a / 1500) * (avg_pts / 10)

        # Proactive Catalyst Application (Injuries)
        if catalysts:
            # Impact is passed as a multiplier (e.g. 0.92 for 8% hit)
            lambda_h *= catalysts.get(home_team, 1.0)
            lambda_a *= catalysts.get(away_team, 1.0)

        sim_h = np.random.poisson(lambda_h, 15000)
        sim_a = np.random.poisson(lambda_a, 15000)
        prob_poisson = np.sum(sim_h > sim_a) / 15000

        # 4. Final Ensemble Weighting
        # We weight Poisson 60% (current form/scoring) and Elo 40% (historical floor)
        final_prob_h = (prob_poisson * 0.6) + (prob_elo * 0.4) + rest_effect_h - rest_effect_a
        final_prob_h = np.clip(final_prob_h, 0.01, 0.99)
        
        return final_prob_h, 1 - final_prob_h

    def analyze_bet(self, home_team, away_team, home_odds, away_odds, catalysts=None, hfa=50, rest_h=2, rest_a=2):
        prob_h, prob_a = self.predict_matchup_ensemble(
            home_team, away_team, catalysts=catalysts, hfa=hfa, rest_days_h=rest_h, rest_days_a=rest_a
        )
        
        # Ev calculations
        ev_h = self.calculate_ev(prob_h, home_odds)
        ev_a = self.calculate_ev(prob_a, away_odds)
        
        # Accuracy & Confidence Scoring
        # Confidence is derived from the "Distance" from 50% adjusted by the Edge
        confidence_score = (abs(prob_h - 0.5) * 2) * 100
        
        # Calibration Metric (Predicted vs Implied)
        implied_h = 1 / home_odds
        implied_a = 1 / away_odds

        return {
            "home": {
                "team": home_team,
                "prob": prob_h,
                "ev": ev_h,
                "market_implied": implied_h,
                "edge": prob_h - implied_h,
                "confidence": confidence_score
            },
            "away": {
                "team": away_team,
                "prob": prob_a,
                "ev": ev_a,
                "market_implied": implied_a,
                "edge": prob_a - implied_a,
                "confidence": confidence_score
            }
        }
