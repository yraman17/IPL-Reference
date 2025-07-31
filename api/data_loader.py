import pandas as pd
import os

def load_data():
    """Load CSV data with error handling"""
    try:
        batting_df = pd.read_csv("player_data/batting_stats.csv")
        bowling_df = pd.read_csv("player_data/bowling_stats.csv")
        career_batting_df = pd.read_csv("player_data/career_batting_stats.csv")
        career_bowling_df = pd.read_csv("player_data/career_bowling_stats.csv")
        
        print("Data loaded successfully!")
        print(f"batting_df: {batting_df.shape}, columns: {batting_df.columns.tolist()}")
        print(f"bowling_df: {bowling_df.shape}, columns: {bowling_df.columns.tolist()}")
        print(f"career_batting_df: {career_batting_df.shape}, columns: {career_batting_df.columns.tolist()}")
        print(f"career_bowling_df: {career_bowling_df.shape}, columns: {career_bowling_df.columns.tolist()}")
        return batting_df, bowling_df, career_batting_df, career_bowling_df
    except FileNotFoundError as e:
        print(f"Error: CSV files not found. Please run the data processing scripts first.")
        print(f"Missing file: {e}")
        return None, None, None, None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None

# Load data when module is imported
batting_df, bowling_df, career_batting_df, career_bowling_df = load_data()