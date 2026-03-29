try:
    import nfl_data_py as nfl
except ImportError:
    print("nfl_data_py not installed. Please run pip install nfl_data_py")

import pandas as pd

class NFLFetcher:
    @staticmethod
    def get_recent_games(years=[2023, 2024]):
        """
        Fetches historical NFL game results.
        """
        all_games = []
        for year in years:
            try:
                # Schedules contain results
                df = nfl.import_schedules([year])
                all_games.append(df)
            except Exception as e:
                print(f"Error fetching NFL {year}: {e}")
                
        if not all_games:
            return pd.DataFrame()
            
        df = pd.concat(all_games)
        
        # NFL Data columns: 'gameday', 'home_team', 'away_team', 'home_score', 'away_score'
        # gameday is YYYY-MM-DD
        
        df = df.rename(columns={'gameday': 'date'})
        # Filter for completed games
        df = df[df['result'].notna()]
        
        return df[['date', 'home_team', 'away_team', 'home_score', 'away_score']]
