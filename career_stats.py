import pandas as pd
import numpy as np

def load_career_stats():
    """
    Load and aggregate career stats from existing CSV files.
    
    This function processes season-by-season statistics to calculate
    career totals and averages for all players.
    """
    
    # Load the existing CSV files
    batting_df = pd.read_csv("player_data/batting_stats.csv")
    bowling_df = pd.read_csv("player_data/bowling_stats.csv")

    # Ensure numeric columns are correct type
    batting_numeric_cols = ['matches', 'innings', 'not_outs', 'runs', 'balls', '50s', '100s', '4s', '6s', 'catches', 'stumpings']
    for col in batting_numeric_cols:
        batting_df[col] = pd.to_numeric(batting_df[col], errors='coerce')

    bowling_numeric_cols = ['matches', 'innings', 'balls_bowled', 'runs_conceded', 'wickets', '3w_hauls', '4w_hauls', '5w_hauls']
    for col in bowling_numeric_cols:
        bowling_df[col] = pd.to_numeric(bowling_df[col], errors='coerce')
    
    # Group by player and aggregate career stats
    career_batting = batting_df.groupby('player').agg({
        'team': lambda x: ', '.join(set(x)),  # All teams played for
        'matches': 'sum',
        'innings': 'sum',
        'not_outs': 'sum',
        'runs': 'sum',
        'balls': 'sum',
        '50s': 'sum',
        '100s': 'sum',
        '4s': 'sum',
        '6s': 'sum',
        'catches': 'sum',
        'stumpings': 'sum'
    }).reset_index()
    
    career_bowling = bowling_df.groupby('player').agg({
        'team': lambda x: ', '.join(set(x)),  # All teams played for
        'matches': 'sum',
        'innings': 'sum',
        'balls_bowled': 'sum',
        'runs_conceded': 'sum',
        'wickets': 'sum',
        '3w_hauls': 'sum',
        '4w_hauls': 'sum',
        '5w_hauls': 'sum'
    }).reset_index()
    
    # Calculate career averages and rates
    career_batting['batting_average'] = np.where(
        (career_batting['innings'] - career_batting['not_outs']) > 0,
        round(career_batting['runs'] / (career_batting['innings'] - career_batting['not_outs']), 2),
        0.0
    )
    
    career_batting['strike_rate'] = np.where(
        career_batting['balls'] > 0,
        round((career_batting['runs'] * 100) / career_batting['balls'], 2),
        0.0
    )
    
    career_bowling['bowling_average'] = np.where(
        career_bowling['wickets'] > 0,
        round(career_bowling['runs_conceded'] / career_bowling['wickets'], 2),
        0.0
    )
    
    career_bowling['economy_rate'] = np.where(
        career_bowling['balls_bowled'] > 0,
        round(career_bowling['runs_conceded'] / (career_bowling['balls_bowled'] / 6), 2),
        0.0
    )
    
    career_bowling['strike_rate'] = np.where(
        career_bowling['wickets'] > 0,
        round(career_bowling['balls_bowled'] / career_bowling['wickets'], 2),
        0.0
    )
    
    # Find career best bowling from individual season data
    best_bowling_data = bowling_df[bowling_df['best_bowling'] != ''].copy()
    if not best_bowling_data.empty:
        best_bowling_data['wickets'] = best_bowling_data['best_bowling'].str.extract(r'BB: (\d+)/').astype('Int64')
        best_bowling_data['runs'] = best_bowling_data['best_bowling'].str.extract(r'/(\d+)').astype('Int64')
        
        # Find best bowling for each player
        career_best_list = []
        for player in career_bowling['player']:
            player_data = best_bowling_data[best_bowling_data['player'] == player]
            if not player_data.empty:
                # Find the best bowling (most wickets, then least runs)
                try:
                    best_idx = player_data['wickets'].idxmax()
                    if pd.isna(best_idx):
                        best_idx = player_data['runs'].idxmin()
                    career_best_list.append({
                        'player': player,
                        'best_bowling': player_data.loc[best_idx, 'best_bowling']
                    })
                except (ValueError, KeyError):
                    career_best_list.append({
                        'player': player,
                        'best_bowling': ''
                    })
            else:
                career_best_list.append({
                    'player': player,
                    'best_bowling': ''
                })
        
        career_best_df = pd.DataFrame(career_best_list)
        career_bowling = career_bowling.merge(career_best_df, on='player', how='left')
    else:
        career_bowling['best_bowling'] = ''
    
    # Find career high score from individual season data
    high_score_data = batting_df.copy()
    high_score_data['high_score_num'] = pd.to_numeric(high_score_data['high_score'].str.replace('*', ''), errors='coerce')
    
    # Find high score for each player
    career_high_score_list = []
    for player in career_batting['player']:
        player_data = high_score_data[high_score_data['player'] == player]
        if not player_data.empty:
            # Find the highest score
            try:
                best_idx = player_data['high_score_num'].idxmax()
                if not pd.isna(best_idx):
                    career_high_score_list.append({
                        'player': player,
                        'high_score': player_data.loc[best_idx, 'high_score']
                    })
                else:
                    career_high_score_list.append({
                        'player': player,
                        'high_score': ''
                    })
            except (ValueError, KeyError):
                career_high_score_list.append({
                    'player': player,
                    'high_score': ''
                })
        else:
            career_high_score_list.append({
                'player': player,
                'high_score': ''
            })
    
    career_high_score_df = pd.DataFrame(career_high_score_list)
    career_batting = career_batting.merge(career_high_score_df, on='player', how='left')
    
    # After all calculations, set '-' for batsmen with 0 innings
    mask_bat = career_batting['innings'] == 0
    career_batting.loc[mask_bat, ['not_outs', 'high_score', 'strike_rate', 'batting_average']] = '-'

    # For bowlers with 0 innings, set '-' for bowling_average, strike_rate, best_bowling
    mask_bowl = career_bowling['innings'] == 0
    career_bowling.loc[mask_bowl, ['bowling_average', 'strike_rate', 'best_bowling']] = '-'

    return career_batting, career_bowling

def save_career_stats(career_batting, career_bowling):
    """Save career stats to CSV files"""
    
    # Reorder columns for better readability
    batting_columns = [
        'player', 'team', 'matches', 'innings', 'not_outs', 'runs', 'balls',
        'batting_average', 'strike_rate', 'high_score', '50s', '100s', 
        '4s', '6s', 'catches', 'stumpings'
    ]
    
    bowling_columns = [
        'player', 'team', 'matches', 'innings', 'balls_bowled', 
        'runs_conceded', 'wickets', 'bowling_average', 'economy_rate', 
        'strike_rate', '3w_hauls', '4w_hauls', '5w_hauls', 'best_bowling'
    ]
    
    career_batting[batting_columns].to_csv("player_data/career_batting_stats.csv", index=False)
    career_bowling[bowling_columns].to_csv("player_data/career_bowling_stats.csv", index=False)
    
    print("Career stats saved to player_data/career_batting_stats.csv and player_data/career_bowling_stats.csv")

if __name__ == "__main__":
    print("Loading and aggregating career stats...")
    career_batting, career_bowling = load_career_stats()
    
    print("Saving career stats...")
    save_career_stats(career_batting, career_bowling)
    
    print("Done!") 