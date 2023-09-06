from pybaseball import statcast_pitcher_exitvelo_barrels, statcast_pitcher_pitch_arsenal, statcast_pitcher_arsenal_stats

# get data for pitchers with a minimum of 100 batted ball events in 2019
# data = statcast_pitcher_exitvelo_barrels(2019, 0)

data = statcast_pitcher_arsenal_stats(2023, minPA=0)

data.to_csv('arsenal.csv', sep='|', index=False)

print(data)
