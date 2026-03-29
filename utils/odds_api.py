import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class OddsAPI:
    BASE_URL = "https://api.the-odds-api.com/v4/sports"
    API_KEY = os.getenv("ODDS_API_KEY")

    @classmethod
    def get_odds(cls, sport="americanfootball_nfl", regions="us", markets="h2h"):
        """
        Fetch odds for a specific sport.
        Sports: 
        - basketball_nba
        - americanfootball_nfl
        - baseball_mlb
        - icehockey_nhl
        """
        url = f"{cls.BASE_URL}/{sport}/odds"
        params = {
            "api_key": cls.API_KEY,
            "regions": regions,
            "markets": markets,
            "oddsFormat": "decimal"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching odds: {e}")
            return []

    @classmethod
    def parse_odds(cls, odds_data):
        """
        Parses the raw JSON odds into a clean DataFrame.
        """
        parsed = []
        for game in odds_data:
            home_team = game.get("home_team")
            away_team = game.get("away_team")
            commence_time = game.get("commence_time")
            
            # Find the best odds across bookmakers
            bookmakers = game.get("bookmakers", [])
            for book in bookmakers:
                market = book.get("markets", [{}])[0]
                outcomes = market.get("outcomes", [])
                
                prices = {o["name"]: o["price"] for o in outcomes}
                
                parsed.append({
                    "id": game.get("id"),
                    "sport": game.get("sport_key"),
                    "commence_time": commence_time,
                    "home_team": home_team,
                    "away_team": away_team,
                    "bookmaker": book.get("title"),
                    "home_price": prices.get(home_team),
                    "away_price": prices.get(away_team),
                    "draw_price": prices.get("Draw") if "Draw" in prices else None
                })
        return pd.DataFrame(parsed)
