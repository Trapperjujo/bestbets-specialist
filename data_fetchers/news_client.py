import requests
import json
import os
from datetime import datetime

class NewsIntelligence:
    """
    Fetches real-time sports news and injury reports.
    Provides data to the predictive model for catalyst weighting.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2" if self.api_key else None

    def get_headlines(self, sport: str = "sports"):
        """
        Fetches top sports headlines.
        """
        if not self.api_key:
            return self._get_mock_news(sport)
            
        params = {
            "q": sport,
            "category": "sports",
            "language": "en",
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/top-headlines", params=params)
            if response.status_code == 200:
                return response.json().get('articles', [])
            return self._get_mock_news(sport)
        except Exception:
            return self._get_mock_news(sport)

    def get_injury_reports(self, league: str):
        """
        Fetches official injury reports. 
        In a production environment, this would hit balldontlie.io or SportsDataIO.
        """
        # Placeholder for league-specific injury data
        mock_injuries = {
            "NBA": [
                {"player": "Joel Embiid", "team": "76ers", "status": "Out", "reason": "Knee"},
                {"player": "Tyrese Haliburton", "team": "Pacers", "status": "Questionable", "reason": "Hamstring"}
            ],
            "NFL": [
                {"player": "Lamar Jackson", "team": "Ravens", "status": "Probable", "reason": "Illness"}
            ],
            "MLB": [
                {"player": "Shohei Ohtani", "team": "Dodgers", "status": "Questionable", "reason": "Elbow"}
            ],
            "NHL": [
                 {"player": "Connor McDavid", "team": "Oilers", "status": "Out", "reason": "Upper Body"}
            ]
        }
        return mock_injuries.get(league.upper(), [])

    def _get_mock_news(self, sport: str):
        """Fallback for simulation or when API key is missing."""
        return [
            {
                "title": f"The Evolution of {sport} Analytics in the Modern Era",
                "description": "How high-fidelity data is changing the way teams evaluate talent.",
                "url": "#",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": f"Upcoming Playoff Implications for {sport} Contenders",
                "description": "A look at the current standings and what teams need to secure a spot.",
                "url": "#",
                "publishedAt": datetime.now().isoformat()
            }
        ]

if __name__ == "__main__":
    client = NewsIntelligence()
    print(f"Injuries: {client.get_injury_reports('NBA')}")
    print(f"News: {len(client.get_headlines('NBA'))} articles found.")
