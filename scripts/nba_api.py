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

nba_teams_colors = {
    'Atlanta Hawks': ['#E03A39', '#F1C30F', '#003A6C'],
    'Boston Celtics': ['#007A33', '#FFFFFF', '#000000'],
    'Brooklyn Nets': ['#000000', '#FFFFFF', '#BDC0C0'],
    'Charlotte Hornets': ['#1D1160', '#A1A9B0', '#00B2A9'],
    'Chicago Bulls': ['#CE1141', '#000000', '#FFFFFF'],
    'Cleveland Cavaliers': ['#6F263D', '#FFB81C', '#000000'],
    'Dallas Mavericks': ['#00538C', '#B8C4CA', '#000000'],
    'Denver Nuggets': ['#0E76A8', '#FEC524', '#B3B3B3'],
    'Detroit Pistons': ['#006BB6', '#C8102E', '#FFFFFF'],
    'Golden State Warriors': ['#006BB6', '#FDB927', '#FFFFFF'],
    'Houston Rockets': ['#CE1141', '#000000', '#A2A9AF'],
    'Indiana Pacers': ['#002D72', '#F7E03C', '#003F6C'],
    'Los Angeles Clippers': ['#ED0A3F', '#002A5C', '#FFFFFF'],
    'Los Angeles Lakers': ['#552583', '#F1C40F', '#FFFFFF'],
    'Memphis Grizzlies': ['#5D76A9', '#121F3E', '#7F8C8D'],
    'Miami Heat': ['#98002E', '#F9A01B', '#000000'],
    'Milwaukee Bucks': ['#00471B', '#EEE1C6', '#AB8A5F'],
    'Minnesota Timberwolves': ['#00471B', '#007A33', '#003A6C'],
    'New Orleans Pelicans': ['#0C2340', '#006BB6', '#F1C30F'],
    'New York Knicks': ['#006BB6', '#F68428', '#FFFFFF'],
    'Oklahoma City Thunder': ['#007AC1', '#F05133', '#F3A800'],
    'Orlando Magic': ['#0077C0', '#0060A0', '#C4CED4'],
    'Philadelphia 76ers': ['#006AB6', '#ED174C', '#FFFFFF'],
    'Phoenix Suns': ['#1D1160', '#E56020', '#F1C40F'],
    'Portland Trail Blazers': ['#E03A39', '#000000', '#C4CED4'],
    'Sacramento Kings': ['#5A2D81', '#000000', '#FFFFFF'],
    'San Antonio Spurs': ['#000000', '#C4CED4', '#E0E0E0'],
    'Toronto Raptors': ['#C8102E', '#000000', '#6F263D'],
    'Utah Jazz': ['#002B5C', '#00471B', '#F9A01B'],
    'Washington Wizards': ['#002F6C', '#E03A39', '#C4CED4'],
}

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to create the quadrant chart
def quadrant_chart(team_name, x, y, xtick_labels=None, ytick_labels=None, data_labels=None,
                   highlight_quadrants=None, result_labels=None, ax=None, leagueAvg=None):
    logging.info("Starting quadrant_chart function")
    
    matplotlib.use('Agg')

    # Ensure ax is passed or create one
    if ax is None:
        logging.info("No ax provided, creating new figure and axes")
        fig, ax = plt.subplots(figsize=(12, 8))  # Increased figure size for better space
    else:
        logging.info("Using provided ax")

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

    # Create a DataFrame with the x, y, and result columns
    try:
        logging.info("Creating DataFrame from x, y, and result labels")
        data = pd.DataFrame({'x': x, 'y': y, 'result': result_labels})
    except Exception as e:
        logging.error(f"Error while creating DataFrame: {e}")
        raise e

    # Group data and calculate necessary fields
    try:
        logging.info("Grouping data to identify duplicates and calculating win ratios")
        group_data = data.groupby(['x', 'y', 'result']).size().unstack(fill_value=0).reset_index()
        group_data['total_count'] = group_data['W'] + group_data['L']
        group_data['win_ratio'] = group_data['W'] / group_data['total_count']
    except Exception as e:
        logging.error(f"Error while processing grouped data: {e}")
        raise e

    # Set limits for x and y axes
    try:
        logging.info("Setting x and y axis limits")
        y_avg = data['y'].mean()
        x_avg = data['x'].mean()

        adj_x = max((data['x'].max() - x_avg), (x_avg - data['x'].min())) * 1.1
        lb_x, ub_x = (x_avg - adj_x, x_avg + adj_x)
        ax.set_xlim(lb_x, ub_x)

        adj_y = max((data['y'].max() - y_avg), (y_avg - data['y'].min())) * 1.1
        lb_y, ub_y = (y_avg - adj_y, y_avg + adj_y)
        ax.set_ylim(lb_y, ub_y)
    except Exception as e:
        logging.error(f"Error while setting axis limits: {e}")
        raise e

    # Set tick labels if provided
    try:
        if xtick_labels:
            logging.info("Setting custom x-axis tick labels")
            ax.set_xticks([lb_x, (x_avg - adj_x / 2), x_avg, (x_avg + adj_x / 2), ub_x])
            ax.set_xticklabels([np.round(lb_x, 2), np.round((x_avg - adj_x / 2), 2), np.round(x_avg, 2),
                                np.round((x_avg + adj_x / 2), 2), np.round(ub_x, 2)])

        if ytick_labels:
            logging.info("Setting custom y-axis tick labels")
            ax.set_yticks([lb_y, (y_avg - adj_y / 2), y_avg, (y_avg + adj_y / 2), ub_y])
            ax.set_yticklabels([np.round(lb_y, 2), np.round((y_avg - adj_y / 2), 2), np.round(y_avg, 2),
                                np.round((y_avg + adj_y / 2), 2), np.round(ub_y, 2)])
    except Exception as e:
        logging.error(f"Error while setting tick labels: {e}")
        raise e

    # Plot each point in the group_data with size based on total_count and color based on win_ratio
    try:
        logging.info("Plotting data points on scatter plot")
        for index, row in group_data.iterrows():
            win_color = np.array(matplotlib.colors.to_rgb(nba_teams_colors[team_name][0]))  # Win color
            loss_color = np.array(matplotlib.colors.to_rgb(nba_teams_colors[team_name][1]))  # Loss color
            mix_color = win_color * row['win_ratio'] + loss_color * (1 - row['win_ratio'])  # Mixed color

            # Scatter plot with size proportional to total_count
            ax.scatter(x=row['x'], y=row['y'], linewidth=0.5, edgecolor=nba_teams_colors[team_name][2],
                       color=mix_color, s=20 + row['total_count'] * 10, zorder=99)
    except Exception as e:
        logging.error(f"Error while plotting data points: {e}")
        raise e

    # Add quadrant lines and league average markers
    try:
        logging.info("Adding quadrant lines and league average markers")
        ax.axvline(x_avg, c='k', lw=1)
        ax.axhline(y_avg, c='k', lw=1)
    except Exception as e:
        logging.error(f"Error while adding quadrant lines: {e}")
        raise e

    # Set labels and title
    try:
        logging.info("Setting axis labels and chart title")
        x_label = f'{team_name} {x.name.split(":")[0].replace("Home", "")}'  # Example: Miami Heat Rebounds
        y_label = f'{team_name} Opponent {y.name.split(":")[0].replace("Opponent", "")}'  # Example: Miami Heat Opponent Rebounds
        ax.set_xlabel(x_label, fontsize=14)
        ax.set_ylabel(y_label, fontsize=14)
        title = f'{team_name} {x.name.split(":")[0]} vs {y.name.split(":")[0]}'
        ax.set_title(title, fontsize=16)
    except Exception as e:
        logging.error(f"Error while setting labels or title: {e}")
        raise e

    # Add custom legend
    try:
        logging.info("Adding custom legend")
        win_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=nba_teams_colors[team_name][0], markersize=10, label='Win')
        loss_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=nba_teams_colors[team_name][1], markersize=10, label='Loss')
        ax.legend(handles=[win_patch, loss_patch], loc='best', title="Game Results")
    except Exception as e:
        logging.error(f"Error while adding custom legend: {e}")
        raise e

    # Finalize plot adjustments
    try:
        logging.info("Finalizing plot and saving to buffer")
        ax.set_facecolor('#999999')
        fig.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
    except Exception as e:
        logging.error(f"Error while finalizing and saving the plot: {e}")
        raise e

    logging.info("quadrant_chart function completed successfully")
    return buf

def generate_plot(nba_team, team_stat, opponent_stat):

    try:
        logging.info(f"Starting plot generation for team: {nba_team}, team_stat: {team_stat}, opponent_stat: {opponent_stat}")
        
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

        # Remove duplicates
        AllGames = AllGames[~AllGames.index.duplicated(keep='first')]
        AllOpponentGames = AllOpponentGames[~AllOpponentGames.index.duplicated(keep='first')]
        WinLoss = WinLoss[~WinLoss.index.duplicated(keep='first')]

        merged_df = pd.concat([AllGames, AllOpponentGames, WinLoss], axis=1)
        merged_df.dropna(inplace=True)
        logging.info(f"Merged DataFrame shape: {merged_df.shape}")

        x = merged_df[AllGames.name]
        y = merged_df[AllOpponentGames.name]
        result_labels = merged_df['WL']
        logging.info(f"Data extracted from merged Dataframe: {nba_team}.")

        # Calculate the league average for both stats
        leagueAvgTeam = x.mean()
        leagueAvgOpponent = y.mean()

        buf = quadrant_chart(nba_team, x, y, result_labels=result_labels, leagueAvg=leagueAvgTeam)
        logging.info(f"Plot successfully generated for team: {nba_team}.")

        return buf

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
