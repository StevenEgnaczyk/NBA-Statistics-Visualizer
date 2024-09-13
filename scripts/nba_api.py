from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mplcursors
from io import BytesIO
import logging
import requests

# Proxy settings
PROXY = {
    'http': '162.223.90.130:80',
}

# Proxy request function
def fetch_data_with_proxy(url, params=None):
    try:
        response = requests.get(url, params=params, proxies=PROXY, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

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
    """
    Create the classic four-quadrant chart.
    Args:
        x -- array-like, the x-coordinates to plot
        y -- array-like, the y-coordinates to plot
        xtick_labels -- list, default: None, a two-value list xtick labels
        ytick_labels -- list, default: None, a two-value list of ytick labels
        data_labels -- array-like, default: None, data point annotations
        highlight_quadrants -- list, default: None, list of quadrants to
            emphasize (quadrants are numbered 1-4)
        result_labels -- array-like, default: None, labels indicating 'w' (win) or 'l' (lose)
        ax -- matplotlib.axes object, default: None, the user can pass their own
            axes object if desired
    """
    # allow the user to specify their axes
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

    data = pd.DataFrame({'x': x, 'y': y, 'result': result_labels})

    # calculate averages up front to avoid repeated calculations
    y_avg = data['y'].mean()
    x_avg = data['x'].mean()

    # set x limits
    adj_x = max((data['x'].max() - x_avg), (x_avg - data['x'].min())) * 1.1
    lb_x, ub_x = (x_avg - adj_x, x_avg + adj_x)
    ax.set_xlim(lb_x, ub_x)

    # set y limits
    adj_y = max((data['y'].max() - y_avg), (y_avg - data['y'].min())) * 1.1
    lb_y, ub_y = (y_avg - adj_y, y_avg + adj_y)
    ax.set_ylim(lb_y, ub_y)

    xLabelValues = [lb_x, (x_avg - adj_x / 2), x_avg, (x_avg + adj_x / 2), ub_x]
    xLabels = [np.round(lb_x, 2), np.round((x_avg - adj_x / 2), 2), np.round(x_avg, 2), np.round((x_avg + adj_x / 2), 2), np.round(ub_x, 2)]

    # set x tick labels
    if xtick_labels:
        ax.set_xticks(xLabelValues)
        ax.set_xticklabels(xLabels)

    yLabelValues = [lb_y, (y_avg - adj_y / 2), y_avg, (y_avg + adj_y / 2), ub_y]
    yLabels = [np.round(lb_y, 2), np.round((y_avg - adj_y / 2), 2), np.round(y_avg, 2), np.round((y_avg + adj_y / 2), 2), np.round(ub_y, 2)]

    # set y tick labels
    if ytick_labels:
        ax.set_yticks(yLabelValues)
        ax.set_yticklabels(yLabels)

    # plot remaining points and quadrant lines
    for result, color in zip(['W', 'L'], ['#002D62', '#FDBB30']):
        subset_data = data[data['result'] == result]
        ax.scatter(x=subset_data['x'], y=subset_data['y'], linewidth=0.25, edgecolor='blue', c=color, zorder=99, s=15, label=result.upper())

    ax.axvline(x_avg, c='k', lw=1)
    ax.axhline(y_avg, c='k', lw=1)

    ax.scatter(x=leagueAvg, y=leagueAvg, s=10, c='black', label="League Average")
    ax.plot([lb_x, leagueAvg, ub_x], [lb_y, leagueAvg, ub_y], linestyle='--', color='black')

    # add legend
    ax.legend()

    ax.set_facecolor('#BEC0C2')
    mplcursors.cursor(hover=True)
    
    # save the plot to a BytesIO object
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
        
        # Find the home team ID using proxy
        team_info = fetch_data_with_proxy('https://stats.nba.com/api/v1/teams/')
        if not team_info:
            logging.error(f"Team {nba_team} not found.")
            return None
        team_id = next((team['id'] for team in team_info['data'] if team['full_name'] == nba_team), None)
        if team_id is None:
            logging.error(f"Team {nba_team} not found.")
            return None
        logging.info(f"Team ID for {nba_team}: {team_id}")

        # Get all the games for the home team using proxy
        HomeTeamGameFinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
        url = HomeTeamGameFinder.endpoint
        all_games = fetch_data_with_proxy(url)
        if not all_games:
            logging.error("Failed to fetch home team game data.")
            return None
        AllGames = pd.DataFrame(all_games['resultSets'][0]['rowSet'], columns=all_games['resultSets'][0]['headers']).dropna().set_index('GAME_ID')
        logging.info(f"Fetched {len(AllGames)} games for {nba_team}.")

        # HomeTeam WL
        WinLoss = AllGames['WL']
        logging.info("Win/Loss data retrieved.")

        # Only care about the selected stat
        if team_stat not in stat_rename_dict:
            logging.error(f"Invalid team stat: {team_stat}")
            return None
        AllGames = AllGames[stat_rename_dict[team_stat]]
        AllGames.name = home_team_stat_rename_dict.get(AllGames.name)
        logging.info(f"Team stat data for {team_stat} extracted.")

        # Fetch game logs for the opponents using proxy
        OpponentTeamGames = leaguegamefinder.LeagueGameFinder(vs_team_id_nullable=team_id)
        url = OpponentTeamGames.endpoint
        all_opponent_games = fetch_data_with_proxy(url)
        if not all_opponent_games:
            logging.error("Failed to fetch opponent game data.")
            return None
        AllOpponentGames = pd.DataFrame(all_opponent_games['resultSets'][0]['rowSet'], columns=all_opponent_games['resultSets'][0]['headers']).dropna().set_index('GAME_ID')
        logging.info(f"Fetched {len(AllOpponentGames)} games for opponents of {nba_team}.")

        # Only care about the selected stat
        if opponent_stat not in stat_rename_dict:
            logging.error(f"Invalid opponent stat: {opponent_stat}")
            return None
        AllOpponentGames = AllOpponentGames[stat_rename_dict[opponent_stat]]
        AllOpponentGames.name = away_team_stat_rename_dict.get(AllOpponentGames.name)
        logging.info(f"Opponent stat data for {opponent_stat} extracted.")

        # Merge data
        gameLogs = pd.merge(AllGames, AllOpponentGames, left_index=True, right_index=True)
        gameLogs = pd.merge(gameLogs, WinLoss, left_index=True, right_index=True)
        logging.info(f"Successfully merged game data. {len(gameLogs)} games merged.")

        # Generate the plot
        image = quadrant_chart(gameLogs[AllGames.name], gameLogs[AllOpponentGames.name], result_labels=gameLogs['WL'])
        logging.info("Quadrant chart generated successfully.")
        
        return image

    except Exception as e:
        logging.error(f"Error in generate_plot: {e}", exc_info=True)
        return None
