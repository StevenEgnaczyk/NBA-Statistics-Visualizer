import nba_api
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mplcursors
from io import BytesIO
import logging
from requests import Session

# Proxy configuration (replace with actual proxies)
proxies = {
    'http': '162.223.90.130:80',
}

# Dictionary for renaming stats
stat_rename_dict = {
    'Points': 'PTS',
    'Field Goals Made': 'FGM',
    'Field Goals Attempted': 'FGA',
    'Field Goal Percentage': 'FG_PCT',
    '3 Pointers Made': 'FG3M',
    '3 Pointers Attempted': 'FG3A',
    '3-Point Percentage': 'FG3_PCT',
    'Free Throws Made': 'FTM',
    'Free Throws Attempted': 'FTA',
    'Free Throw Percentage': 'FT_PCT',
    'Offensive Rebounds': 'OREB',
    'Defensive Rebounds': 'DREB',
    'Rebounds': 'REB',
    'Assists': 'AST',
    'Steals': 'STL',
    'Blocks': 'BLK',
    'Turnovers': 'TOV',
    'Personal Fouls': 'PF'
}

home_team_stat_rename_dict = {
    'PTS': 'HomePoints',
    'FGM': 'HomeFGM',
    'FGA': 'HomeFGA',
    'FG_PCT': 'HomeFG%',
    'FG3M': 'Home3PointersMade',
    'FG3A': 'Home3PointersAttempted',
    'FG3_PCT': 'Home3Point%',
    'FTM': 'HomeFreeThrowsMade',
    'FTA': 'HomeFreeThrowsAttempted',
    'FT_PCT': 'HomeFT%',
    'OREB': 'HomeOffensiveRebounds',
    'DREB': 'HomeDefensiveRebounds',
    'REB': 'HomeRebounds',
    'AST': 'HomeAssists',
    'STL': 'HomeSteals',
    'BLK': 'HomeBlocks',
    'TOV': 'HomeTurnovers',
    'PF': 'HomePersonalFouls'
}

away_team_stat_rename_dict = {
    'PTS': 'OpponentPoints',
    'FGM': 'OpponentFGM',
    'FGA': 'OpponentFGA',
    'FG_PCT': 'OpponentFG%',
    'FG3M': 'Opponent3PointersMade',
    'FG3A': 'Opponent3PointersAttempted',
    'FG3_PCT': 'Opponent3Point%',
    'FTM': 'OpponentFreeThrowsMade',
    'FTA': 'OpponentFreeThrowsAttempted',
    'FT_PCT': 'OpponentFT%',
    'OREB': 'OpponentOffensiveRebounds',
    'DREB': 'OpponentDefensiveRebounds',
    'REB': 'OpponentRebounds',
    'AST': 'OpponentAssists',
    'STL': 'OpponentSteals',
    'BLK': 'OpponentBlocks',
    'TOV': 'OpponentTurnovers',
    'PF': 'OpponentPersonalFouls'
}

# Function to create the quadrant chart
def quadrant_chart(x, y, xtick_labels=None, ytick_labels=None, data_labels=None,
                    highlight_quadrants=None, result_labels=None, ax=None, leagueAvg=None):
    matplotlib.use('Agg')
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

    data = pd.DataFrame({'x': x, 'y': y, 'result': result_labels})
    y_avg = data['y'].mean()
    x_avg = data['x'].mean()

    adj_x = max((data['x'].max() - x_avg), (x_avg - data['x'].min())) * 1.1
    lb_x, ub_x = (x_avg - adj_x, x_avg + adj_x)
    ax.set_xlim(lb_x, ub_x)

    adj_y = max((data['y'].max() - y_avg), (y_avg - data['y'].min())) * 1.1
    lb_y, ub_y = (y_avg - adj_y, y_avg + adj_y)
    ax.set_ylim(lb_y, ub_y)

    xLabelValues = [lb_x, (x_avg - adj_x / 2), x_avg, (x_avg + adj_x / 2), ub_x]
    xLabels = [np.round(lb_x, 2), np.round((x_avg - adj_x / 2), 2), np.round(x_avg, 2), np.round((x_avg + adj_x / 2), 2), np.round(ub_x, 2)]

    if xtick_labels:
        ax.set_xticks(xLabelValues)
        ax.set_xticklabels(xLabels)

    yLabelValues = [lb_y, (y_avg - adj_y / 2), y_avg, (y_avg + adj_y / 2), ub_y]
    yLabels = [np.round(lb_y, 2), np.round((y_avg - adj_y / 2), 2), np.round(y_avg, 2), np.round((y_avg + adj_y / 2), 2), np.round(ub_y, 2)]

    if ytick_labels:
        ax.set_yticks(yLabelValues)
        ax.set_yticklabels(yLabels)

    for result, color in zip(['W', 'L'], ['#002D62', '#FDBB30']):
        subset_data = data[data['result'] == result]
        ax.scatter(x=subset_data['x'], y=subset_data['y'], linewidth=0.25, edgecolor='blue', c=color, zorder=99, s=15, label=result.upper())

    ax.axvline(x_avg, c='k', lw=1)
    ax.axhline(y_avg, c='k', lw=1)

    ax.scatter(x=leagueAvg, y=leagueAvg, s=10, c='black', label="League Average")
    ax.plot([lb_x, leagueAvg, ub_x], [lb_y, leagueAvg, ub_y], linestyle='--', color='black')

    ax.legend()
    ax.set_facecolor('#BEC0C2')
    mplcursors.cursor(hover=True)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=500)
    buf.seek(0)
    plt.close()

    return buf

# Configure logging
logging.basicConfig(level=logging.INFO)

def generate_plot(nba_team, team_stat, opponent_stat):

    try:
        logging.info(f"Starting plot generation for team: {nba_team}, team_stat: {team_stat}, opponent_stat: {opponent_stat}")

        # session = Session()
        # session.proxies.update(proxies)  # Set the proxies for the session
        
        # Get all NBA teams using the official API method
        team_info = teams.get_teams()
        if not team_info:
            logging.error("Failed to fetch teams from the NBA API.")
            return None

        team_id = next((team['id'] for team in team_info if team['full_name'] == nba_team), None)
        if team_id is None:
            logging.error(f"Team {nba_team} not found.")
            return None
        logging.info(f"Team ID for {nba_team}: {team_id}")

        logging.info(nba_api.__file__)


        # Get all games for the home team using NBA API
        HomeTeamGameFinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, timeout=15)

        logging.info(HomeTeamGameFinder)
        all_games = HomeTeamGameFinder.get_data_frames()[0]
        if all_games.empty:
            logging.error("Failed to fetch home team game data.")
            return None
        AllGames = all_games.dropna().set_index('GAME_ID')
        logging.info(f"Fetched {len(AllGames)} games for {nba_team}.")

        # HomeTeam WL
        WinLoss = AllGames['WL']
        logging.info("Win/Loss data retrieved.")

        if team_stat not in stat_rename_dict:
            logging.error(f"Invalid team stat: {team_stat}")
            return None
        AllGames = AllGames[stat_rename_dict[team_stat]]
        AllGames.name = home_team_stat_rename_dict.get(AllGames.name)
        logging.info(f"Team stat data for {team_stat} extracted.")

        # Fetch game logs for the opponents using NBA API
        OpponentTeamGames = leaguegamefinder.LeagueGameFinder(vs_team_id_nullable=team_id)
        all_opponent_games = OpponentTeamGames.get_data_frames()[0]
        if all_opponent_games.empty:
            logging.error("Failed to fetch opponent game data.")
            return None
        AllOpponentGames = all_opponent_games.dropna().set_index('GAME_ID')
        logging.info(f"Fetched {len(AllOpponentGames)} games for opponents of {nba_team}.")

        if opponent_stat not in stat_rename_dict:
            logging.error(f"Invalid opponent stat: {opponent_stat}")
            return None
        AllOpponentGames = AllOpponentGames[stat_rename_dict[opponent_stat]]
        AllOpponentGames.name = away_team_stat_rename_dict.get(AllOpponentGames.name)
        logging.info(f"Opponent stat data for {opponent_stat} extracted.")

        # Merge data
        merged_df = pd.concat([AllGames, AllOpponentGames, WinLoss], axis=1)
        merged_df.dropna(inplace=True)
        logging.info(f"Merged DataFrame shape: {merged_df.shape}")

        x = merged_df[AllGames.name]
        y = merged_df[AllOpponentGames.name]
        result_labels = merged_df['WL']

        # Calculate the league average for both stats
        leagueAvgTeam = x.mean()
        leagueAvgOpponent = y.mean()

        buf = quadrant_chart(x, y, result_labels=result_labels, leagueAvg=leagueAvgTeam)
        logging.info(f"Plot successfully generated for team: {nba_team}.")

        return buf

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
