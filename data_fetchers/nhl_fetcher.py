import requests
import pandas as pd

class NHLFetcher:
    """
    Fetches NHL data from the new NHLE API (api-web.nhle.com)
    """
    BASE_URL = "https://api-web.nhle.com/v1"

    @classmethod
    def get_recent_games(cls, seasons=["2023-24", "20242025"]):
        all_games = []
        # Fetch actual schedule
        url = f"{cls.BASE_URL}/schedule/now" 
        try:
            response = requests.get(url)
            data = response.json()
            for week in data.get('gameWeek', []):
                for game in week.get('games', []):
                    # Robust key access
                    if game.get('gameState') in ['OFF', 'FINAL']:
                        all_games.append({
                            'date': game.get('gameDate', 'Unknown'),
                            'home_team': game.get('homeTeam', {}).get('commonName', {}).get('default', 'Unknown'),
                            'away_team': game.get('awayTeam', {}).get('commonName', {}).get('default', 'Unknown'),
                            'home_score': game.get('homeTeam', {}).get('score', 0),
                            'away_score': game.get('awayTeam', {}).get('score', 0)
                        })
        except Exception as e:
            print(f"Error fetching NHL: {e}")
                
        return pd.DataFrame(all_games)
