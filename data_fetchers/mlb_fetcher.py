import pandas as pd
try:
    from pybaseball import league_game_log
except ImportError:
    print("pybaseball not installed.")

class MLBFetcher:
    @staticmethod
    def get_recent_games(years=[2023, 2024]):
        all_games = []
        for year in years:
            try:
                # Fetch both AL and NL
                al = league_game_log(year, league='AL')
                nl = league_game_log(year, league='NL')
                all_games.extend([al, nl])
            except Exception as e:
                print(f"Error fetching MLB {year}: {e}")
        
        if not all_games:
            return pd.DataFrame()
            
        df = pd.concat(all_games)
        # Mapping Baseball-Reference columns to our format
        mapping = {
            'Home': 'home_team',
            'Visitor': 'away_team',
            'HomeScore': 'home_score',
            'VisitorScore': 'away_score',
            'Date': 'date'
        }
        df = df.rename(columns=mapping)
        cols = ['date', 'home_team', 'away_team', 'home_score', 'away_score']
        return df[[c for c in cols if c in df.columns]]
