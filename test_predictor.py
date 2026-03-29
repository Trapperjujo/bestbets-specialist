import sys
import os
sys.path.append(os.getcwd())

from analytics.models import SportsPredictor

def test():
    p = SportsPredictor()
    # Test analyze_bet
    try:
        res = p.analyze_bet("Team A", "Team B", 2.0, 2.0)
        print("Success:", res)
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
