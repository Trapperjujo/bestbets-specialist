import os
import pandas as pd
from data_fetchers.nba_fetcher import NBAFetcher
from data_fetchers.mlb_fetcher import MLBFetcher
from data_fetchers.nfl_fetcher import NFLFetcher
from data_fetchers.nhl_fetcher import NHLFetcher

def main():
    assets_dir = "BESTBETS/assets"
    # Create the directory structure correctly relative to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(script_dir, "assets")
    
    if not os.path.exists(assets_path):
        os.makedirs(assets_path)

    fetchers = {
        "NBA": (NBAFetcher, "nba_history.csv"),
        "MLB": (MLBFetcher, "mlb_history.csv"),
        "NFL": (NFLFetcher, "nfl_history.csv"),
        "NHL": (NHLFetcher, "nhl_history.csv")
    }

    for sport, (fetcher_class, filename) in fetchers.items():
        print(f"Fetching {sport} History...")
        try:
            df = fetcher_class.get_recent_games()
            if not df.empty:
                full_path = os.path.join(assets_path, filename)
                df.to_csv(full_path, index=False)
                print(f"{sport} data saved: {len(df)} games to {full_path}")
            else:
                print(f"No {sport} data found.")
        except Exception as e:
            print(f"{sport} Fetch Failed: {e}")

if __name__ == "__main__":
    main()
