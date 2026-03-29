import pandas as pd
import os
import datetime

class BettingLedger:
    def __init__(self, filename="ledger.csv"):
        self.filename = filename
        self.ledger = self._load_ledger()

    def _load_ledger(self):
        if os.path.exists(self.filename):
            try:
                return pd.read_csv(self.filename)
            except Exception:
                return self._init_ledger()
        else:
            return self._init_ledger()

    def _init_ledger(self):
        """Initializes a new ledger DataFrame with necessary columns."""
        df = pd.DataFrame(columns=[
            "date", "team", "opponent", "stake", "odds", "status", "profit", "equity"
        ])
        return df

    def add_entry(self, team, opponent, stake, odds, status="Pending", profit=0, initial_equity=1000):
        """Adds a new journal entry to the ledger."""
        current_equity = self.ledger["equity"].iloc[-1] if not self.ledger.empty else initial_equity
        
        # In a real app, win/loss status would update profit and equity
        new_entry = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "team": team,
            "opponent": opponent,
            "stake": stake,
            "odds": odds,
            "status": status,
            "profit": profit,
            "equity": current_equity + profit
        }
        
        self.ledger = pd.concat([self.ledger, pd.DataFrame([new_entry])], ignore_index=True)
        self.save()

    def calculate_performance(self):
        """Calculates financial metrics from the ledger."""
        if self.ledger.empty:
            return {"roi": 0, "yield": 0, "sharpe": 0, "drawdown": 0}
            
        total_staked = self.ledger["stake"].sum()
        total_profit = self.ledger["profit"].sum()
        
        roi = total_profit / total_staked if total_staked != 0 else 0
        
        # Simplified Sharpe Ratio (Monthly basis)
        returns = self.ledger["profit"].pct_change().dropna()
        sharpe = (returns.mean() / returns.std() * (12**0.5)) if len(returns) > 1 and returns.std() != 0 else 0
        
        # Max Drawdown
        equity_curve = self.ledger["equity"]
        max_drawdown = (equity_curve.cummax() - equity_curve).max()
        
        return {
            "total_staked": total_staked,
            "total_profit": total_profit,
            "roi": roi,
            "sharpe": sharpe,
            "max_drawdown": max_drawdown
        }

    def save(self):
        self.ledger.to_csv(self.filename, index=False)

if __name__ == "__main__":
    ledger = BettingLedger("test_ledger.csv")
    ledger.add_entry("Lakers", "Warriors", 100, 2.0, status="Win", profit=100)
    print(ledger.calculate_performance())
