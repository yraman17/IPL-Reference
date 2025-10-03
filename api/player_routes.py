from fastapi import APIRouter, HTTPException
from data_loader import batting_df, bowling_df, career_batting_df, career_bowling_df
from typing import List

router = APIRouter()

@router.get("/players")
def get_all_players():
    """Get list of all players"""
    if career_batting_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded. Please run data processing scripts first.")
    
    players = career_batting_df['player'].unique().tolist()
    return {"players": players}

@router.get("/player/{player_name}/batting")
def get_player_batting(player_name: str):
    """Get batting statistics for a specific player across all seasons"""
    if batting_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded. Please run data processing scripts first.")
    
    data = batting_df[batting_df["player"].str.lower() == player_name.lower()]
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
    
    return {
        "player": player_name,
        "batting_stats": data.to_dict(orient="records")
    }

@router.get("/player/{player_name}/bowling")
def get_player_bowling(player_name: str):
    """Get bowling statistics for a specific player across all seasons"""
    if bowling_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded. Please run data processing scripts first.")
    
    data = bowling_df[bowling_df["player"].str.lower() == player_name.lower()]
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
    
    return {
        "player": player_name,
        "bowling_stats": data.to_dict(orient="records")
    }

@router.get("/player/{player_name}/career")
def get_player_career(player_name: str):
    """Get career batting and bowling statistics for a specific player"""
    if career_batting_df is None or career_bowling_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded. Please run data processing scripts first.")
    
    bat = career_batting_df[career_batting_df["player"].str.lower() == player_name.lower()]
    bowl = career_bowling_df[career_bowling_df["player"].str.lower() == player_name.lower()]
    
    if bat.empty and bowl.empty:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
    
    return {
        "player": player_name,
        "career_batting": bat.to_dict(orient="records") if not bat.empty else [],
        "career_bowling": bowl.to_dict(orient="records") if not bowl.empty else []
    }



@router.get("/seasons/{year}/batting")
def get_season_batting(year: str):
    """Get batting leaderboard for a specific season"""
    if batting_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded. Please run data processing scripts first.")
    
    season_data = batting_df[batting_df['season'] == year]
    
    if season_data.empty:
        raise HTTPException(status_code=404, detail=f"No data found for season {year}")
    
    # Sort by runs scored (descending)
    season_data = season_data.sort_values('runs', ascending=False)
    
    return {
        "season": year,
        "batting_leaderboard": season_data.to_dict(orient="records")
    }

@router.get("/seasons/{year}/bowling")
def get_season_bowling(year: str):
    """Get bowling leaderboard for a specific season"""
    if bowling_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded. Please run data processing scripts first.")
    
    season_data = bowling_df[bowling_df['season'] == year]
    
    if season_data.empty:
        raise HTTPException(status_code=404, detail=f"No data found for season {year}")
    
    # Sort by wickets taken (descending)
    season_data = season_data.sort_values('wickets', ascending=False)
    
    return {
        "season": year,
        "bowling_leaderboard": season_data.to_dict(orient="records")
    }
