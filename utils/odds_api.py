import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class OddsAPI:
    BASE_URL = "https://api.the-odds-api.com/v4/sports"
    API_KEY = os.getenv("ODDS_API_KEY")

    @classmethod
    def get_odds(cls, sport="americanfootball_nfl", regions="us,uk,eu,au", markets="h2h"):
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
        Parses raw JSON odds into a clean DataFrame with the BEST prices across ALL books.
        """
        parsed = []
        for game in odds_data:
            game_id = game.get("id")
            home_team = game.get("home_team")
            away_team = game.get("away_team")
            commence_time = game.get("commence_time")
            
            # Aggregate best prices across all bookmakers
            best_home_price = 0
            best_away_price = 0
            best_home_book = ""
            best_away_book = ""
            
            bookmakers = game.get("bookmakers", [])
            for book in bookmakers:
                market = book.get("markets", [{}])[0]
                outcomes = market.get("outcomes", [])
                
                prices = {o["name"]: o["price"] for o in outcomes}
                h_price = prices.get(home_team, 0)
                a_price = prices.get(away_team, 0)
                
                if h_price > best_home_price:
                    best_home_price = h_price
                    best_home_book = book.get("title")
                if a_price > best_away_price:
                    best_away_price = a_price
                    best_away_book = book.get("title")
                    
            if best_home_price > 0:
                parsed.append({
                    "id": game_id,
                    "sport": game.get("sport_key"),
                    "commence_time": commence_time,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_price": best_home_price,
                    "home_book": best_home_book,
                    "away_price": best_away_price,
                    "away_book": best_away_book
                })
        return pd.DataFrame(parsed)
