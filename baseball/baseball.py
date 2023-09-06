import pandas as pd
import os
from pybaseball import schedule_and_record

csv_file_path = 'mlb_130.csv'
if os.path.exists(csv_file_path):
    existing_df = pd.read_csv(csv_file_path)
    existing_df = existing_df.head(1)
    existing_df.to_csv(csv_file_path, index=False)

teams = {
  "BOS": "Boston Red Sox",
  "NYY": "New York Yankees",
  "TB": "Tampa Bay Rays",
  "TOR": "Toronto Blue Jays",
  "BAL": "Baltimore Orioles",
  "CHW": "Chicago White Sox",
  "CLE": "Cleveland Guardians",
  "DET": "Detroit Tigers",
  "KC": "Kansas City Royals",
  "MIN": "Minnesota Twins",
  "HOU": "Houston Astros",
  "OAK": "Oakland Athletics",
  "SEA": "Seattle Mariners",
  "LAA": "Los Angeles Angels",
  "TEX": "Texas Rangers",
  "ATL": "Atlanta Braves",
  "NYM": "New York Mets",
  "PHI": "Philadelphia Phillies",
  "MIA": "Miami Marlins",
  "WSN": "Washington Nationals",
  "MIL": "Milwaukee Brewers",
  "STL": "St. Louis Cardinals",
  "CHC": "Chicago Cubs",
  "CIN": "Cincinnati Reds",
  "PIT": "Pittsburgh Pirates",
  "SF": "San Francisco Giants",
  "SD": "San Diego Padres",
  "LAD": "Los Angeles Dodgers",
  "ARI": "Arizona Diamondbacks",
  "COL": "Colorado Rockies"
}


team_records_list = []

for team_abbreviation in teams.keys():
    team_record = schedule_and_record(2023, team_abbreviation)
    team_records_list.append(team_record)
    print("break")
    
team_records_df = pd.concat(team_records_list, ignore_index=True)
team_records_df.to_csv(csv_file_path, index=False)
