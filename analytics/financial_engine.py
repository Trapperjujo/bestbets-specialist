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
    def assess_risk_level(prob, edge):
        """
        Categorizes a bet into Low, Med, or High risk buckets.
        """
        if prob > 0.65 and edge > 0.02:
            return "Low (Safe Lock)"
        elif prob > 0.45 and edge > 0.05:
            return "Med (Strategic Value)"
        elif edge > 0.10:
            return "High (Upset Alert)"
        return "Not Recommended"

if __name__ == "__main__":
    fe = FinancialEngine()
    print(f"Kelly Stake (60% win, 2.0 odds): {fe.calculate_fractional_kelly(0.6, 2.0):.2%}")
    print(f"Risk Level: {fe.assess_risk_level(0.6, 0.08)}")
