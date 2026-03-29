try:
    from nba_api.stats.endpoints import leaguegamefinder
    from nba_api.stats.static import teams
except ImportError:
    print("nba_api not installed. Please run pip install nba_api")

import pandas as pd

class NBAFetcher:
    @staticmethod
    def get_recent_games(seasons=["2023-24", "2024-25"]):
        """
        Fetches historical game results to train the model.
        """
        all_games = []
        for season in seasons:
            gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season, league_id_nullable='00')
            games = gamefinder.get_data_frames()[0]
            all_games.append(games)
        
        df = pd.concat(all_games)
        
        # We need to pair home and away games (NBA API returns one row per team per game)
        # Columns: GAME_ID, TEAM_NAME, MATCHUP, WL, PTS, etc.
        # Matchup: 'TEAM @ TEAM' or 'TEAM vs. TEAM'
        
        # Filter for the relevant columns and pivot to get one row per game
        df = df[['GAME_ID', 'GAME_DATE', 'TEAM_NAME', 'MATCHUP', 'WL', 'PTS']]
        
        # This is a bit complex due to NBA API format. 
        # For simplicity in this demo, we'll return a cleaned version where we have:
        # HomeTeam, AwayTeam, HomeScore, AwayScore
        
        # A simple way to pair:
        df['IS_HOME'] = df['MATCHUP'].apply(lambda x: 'vs.' in x)
        
        home_games = df[df['IS_HOME']].rename(columns={'TEAM_NAME': 'home_team', 'PTS': 'home_score'})
        away_games = df[~df['IS_HOME']].rename(columns={'TEAM_NAME': 'away_team', 'PTS': 'away_score'})
        
        merged = pd.merge(home_games, away_games, on='GAME_ID')
        return merged[['GAME_DATE_x', 'home_team', 'away_team', 'home_score', 'away_score']].rename(columns={'GAME_DATE_x': 'date'})

    @staticmethod
    def get_team_abbreviations():
        nba_teams = teams.get_teams()
        return {team['full_name']: team['abbreviation'] for team in nba_teams}
