import os
import json
from collections import defaultdict
import pandas as pd

DATA_PATH = "ipl_data/"

def load_matches():
    """Load all match JSON files from the ipl_data directory"""
    matches = []
    for fname in os.listdir(DATA_PATH):
        if fname.endswith(".json"):
            with open(os.path.join(DATA_PATH, fname)) as f:
                matches.append(json.load(f))
    return matches

def is_legal_delivery(delivery):
    """Check if delivery is legal (not wide) - no-balls count as balls faced"""
    extras = delivery.get("extras", {})
    return "wides" not in extras

def count_matches_and_innings(matches):
    """Count matches, innings, not outs, runs, high score, balls faced, strike rate, 50s, 100s, 4s, 6s, catches, and stumpings for each player per season"""
    player_stats = defaultdict(lambda: defaultdict(lambda: {
        "matches": set(),
        "innings": set(),  # Track unique innings per match
        "not_outs": set(),  # Track unique not outs per match
        "runs": 0,  # Track total runs scored
        "high_score": 0,  # Track highest score
        "high_score_not_out": False,  # Track if high score was not out
        "balls": 0,  # Track balls faced
        "fifties": 0,  # Track number of 50s
        "hundreds": 0,  # Track number of 100s
        "fours": 0,  # Track number of 4s
        "sixes": 0,  # Track number of 6s
        "catches": 0,  # Track number of catches
        "stumpings": 0,  # Track number of stumpings
        "bowling_innings": set(),  # Track unique bowling innings per match
        "balls_bowled": 0,  # Track balls delivered (excluding wides and no-balls)
        "runs_conceded": 0  # Track runs conceded (batter runs + wides + no-balls)
    }))
    
    for match in matches:
        match_id = f"{match['info']['dates'][0]}_{match['info']['venue']}"
        # Normalize season to string and fix season formats
        season = str(match["info"]["season"])
        if season == "2020/21":
            season = "2020"
        elif season == "2007/08":
            season = "2008"
        elif season == "2009/10":
            season = "2010"
        
        # Get all players from both teams for match count
        for team, players in match["info"]["players"].items():
            for player in players:
                player_stats[player][season]["matches"].add(match_id)
        
        # Track innings, dismissals, and runs for batting stats
        batters_in_match = set()  # Track who batted in this match
        dismissed_in_match = set()  # Track who was dismissed in this match
        runs_in_match = defaultdict(int)  # Track runs per player in this match
        bowlers_in_match = set()  # Track who bowled in this match
        
        for inning in match["innings"]:
            for over in inning["overs"]:
                for delivery in over["deliveries"]:
                    batter = delivery["batter"]
                    bowler = delivery["bowler"]
                    non_striker = delivery.get("non_striker", "")
                    
                    # Add innings for batter and non_striker (unique per match)
                    for player in [batter, non_striker]:
                        if player:  # Skip empty non_striker
                            batters_in_match.add(player)
                    
                    # Add bowling innings (unique per match)
                    bowlers_in_match.add(bowler)
                    
                    # Add balls delivered (excluding wides and no-balls)
                    if is_legal_delivery(delivery):
                        player_stats[bowler][season]["balls_bowled"] += 1
                    
                    # Add runs conceded (batter runs + wides + no-balls only)
                    runs_conceded = delivery["runs"]["batter"]  # Batter's runs
                    if "extras" in delivery:
                        for extra_type, extra_data in delivery["extras"].items():
                            if extra_type in ["wides", "noballs"]:
                                runs_conceded += extra_data.get("runs", 0)
                    player_stats[bowler][season]["runs_conceded"] += runs_conceded
                    
                    # Add runs scored by the batter
                    runs_scored = delivery["runs"]["batter"]
                    player_stats[batter][season]["runs"] += runs_scored
                    runs_in_match[batter] += runs_scored
                    
                    # Count 4s and 6s
                    if runs_scored == 4:
                        player_stats[batter][season]["fours"] += 1
                    elif runs_scored == 6:
                        player_stats[batter][season]["sixes"] += 1
                    
                    # Add balls faced (only legal deliveries)
                    if is_legal_delivery(delivery):
                        player_stats[batter][season]["balls"] += 1
                    
                    # Check for dismissals and fielding stats
                    if "wickets" in delivery:
                        for wicket in delivery["wickets"]:
                            dismissed_in_match.add(wicket["player_out"])
                            
                            # Track catches and stumpings
                            if wicket["kind"] == "caught" and "fielders" in wicket:
                                for fielder in wicket["fielders"]:
                                    player_stats[fielder["name"]][season]["catches"] += 1
                            elif wicket["kind"] == "stumped" and "fielders" in wicket:
                                for fielder in wicket["fielders"]:
                                    player_stats[fielder["name"]][season]["stumpings"] += 1
        
        # Calculate not outs and update high scores
        not_outs = batters_in_match - dismissed_in_match
        for player in not_outs:
            player_stats[player][season]["not_outs"].add(match_id)
        
        # Update high scores and count 50s and 100s for all batters in this match
        for player in batters_in_match:
            runs_in_this_match = runs_in_match[player]
            was_not_out = player in not_outs
            
            # Check if this is a new high score
            if runs_in_this_match > player_stats[player][season]["high_score"]:
                player_stats[player][season]["high_score"] = runs_in_this_match
                player_stats[player][season]["high_score_not_out"] = was_not_out
            elif runs_in_this_match == player_stats[player][season]["high_score"]:
                # If same score, prefer not out version
                if was_not_out and not player_stats[player][season]["high_score_not_out"]:
                    player_stats[player][season]["high_score_not_out"] = True
            
            # Count 50s and 100s
            if runs_in_this_match >= 100:
                player_stats[player][season]["hundreds"] += 1
            elif runs_in_this_match >= 50:
                player_stats[player][season]["fifties"] += 1
        
        # Add innings count for batting
        for player in batters_in_match:
            player_stats[player][season]["innings"].add(match_id)
        
        # Add bowling innings count
        for player in bowlers_in_match:
            player_stats[player][season]["bowling_innings"].add(match_id)
    
    return player_stats

def save_match_counts(player_stats):
    """Save match, innings, not out, run, high score, balls faced, strike rate, 50s, 100s, 4s, 6s, catches, and stumpings counts to CSV files"""
    batting_rows = []
    bowling_rows = []
    
    for player, seasons in player_stats.items():
        for season, stats in seasons.items():
            # Format high score with asterisk if not out
            high_score_str = str(stats["high_score"])
            if stats["high_score_not_out"]:
                high_score_str += "*"
            
            # Calculate strike rate
            strike_rate = 0.0
            if stats["balls"] > 0:
                strike_rate = round((stats["runs"] * 100) / stats["balls"], 2)
            
            batting_row = {
                "player": player,
                "season": season,
                "matches": len(stats["matches"]),
                "innings": len(stats["innings"]),
                "not_outs": len(stats["not_outs"]),
                "runs": stats["runs"],
                "high_score": high_score_str,
                "balls": stats["balls"],
                "strike_rate": strike_rate,
                "50s": stats["fifties"],
                "100s": stats["hundreds"],
                "4s": stats["fours"],
                "6s": stats["sixes"],
                "catches": stats["catches"],
                "stumpings": stats["stumpings"]
            }
            bowling_row = {
                "player": player,
                "season": season,
                "matches": len(stats["matches"]),
                "innings": len(stats["bowling_innings"]),
                "balls_bowled": stats["balls_bowled"],
                "runs_conceded": stats["runs_conceded"]
            }
            batting_rows.append(batting_row)
            bowling_rows.append(bowling_row)
    
    pd.DataFrame(batting_rows).to_csv("batting_stats.csv", index=False)
    pd.DataFrame(bowling_rows).to_csv("bowling_stats.csv", index=False)

if __name__ == "__main__":
    print("Loading match files...")
    matches = load_matches()
    print(f"Loaded {len(matches)} matches.")
    
    print("Counting matches, innings, not outs, runs, high scores, balls faced, strike rates, 50s, 100s, 4s, 6s, catches, and stumpings per player per season...")
    player_stats = count_matches_and_innings(matches)
    
    print("Saving to CSV files...")
    save_match_counts(player_stats)
    print("Done! Created batting_stats.csv and bowling_stats.csv")


