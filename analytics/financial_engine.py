import numpy as np

class FinancialEngine:
    """
    Handles risk management and capital allocation using the Kelly Criterion.
    """
    
    @staticmethod
    def calculate_fractional_kelly(win_prob, decimal_odds, fraction=0.25):
        """
        Calculates the recommended stake using Fractional Kelly Criterion.
        f* = (p * (b + 1) - 1) / b
        Where:
        p: Win Probability
        b: Net Odds (Decimal Odds - 1)
        fraction: Risk multiplier (e.g. 0.25 for 1/4 Kelly)
        """
        if decimal_odds <= 1:
            return 0.0
            
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        
        # Kelly % = (b*p - q) / b
        f_star = (b * p - q) / b
        
        # Apply fractional safety buffer
        recommended_stake_pct = max(0, f_star * fraction)
        return recommended_stake_pct

    @staticmethod
    def calculate_unit_stake(win_prob, edge, confidence_multiplier=1.0):
        """
        Maps win probability and edge to a standard "Unit" system (1-5 units).
        1 Unit = Standard Bet
        3 Units = Strong Confidence
        5 Units = Max Play / Whale
        """
        # Base units on winning probability first, then edge
        base_units = 0
        
        if win_prob >= 0.75:
            base_units = 4
        elif win_prob >= 0.65:
            base_units = 3
        elif win_prob >= 0.58:
            base_units = 2
        elif win_prob >= 0.52:
            base_units = 1
            
        # Add Bonus Units for significant Edge (Value)
        if edge > 0.10:
            base_units += 1
            
        return min(5, base_units * confidence_multiplier)

    @staticmethod
    def assess_risk_level(prob, edge):
        """
        Categorizes a bet into Specialist-Sports buckets.
        """
        if prob > 0.70:
            return "Elite Lock (High Accuracy)"
        elif prob > 0.40 and edge > 0.08:
            return "Strategic Upset (High Value)"
        elif prob > 0.55:
            return "Standard Play"
        return "Low Confidence"

if __name__ == "__main__":
    fe = FinancialEngine()
    print(f"Kelly Stake (60% win, 2.0 odds): {fe.calculate_fractional_kelly(0.6, 2.0):.2%}")
    print(f"Risk Level: {fe.assess_risk_level(0.6, 0.08)}")
