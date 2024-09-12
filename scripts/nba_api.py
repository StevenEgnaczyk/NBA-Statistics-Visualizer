from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mplcursors
from io import BytesIO

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

def quadrant_chart(x, y, xtick_labels=None, ytick_labels=None, data_labels=None,
                    highlight_quadrants=None, result_labels=None, ax=None, leagueAvg = None):
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
    xLabels = [np.round(lb_x,2), np.round((x_avg - adj_x / 2),2), np.round(x_avg,2), np.round((x_avg + adj_x / 2),2), np.round(ub_x,2)]

    # set x tick labels
    if xtick_labels:
        ax.set_xticks(xLabelValues)
        ax.set_xticklabels(xLabels)

    yLabelValues = [lb_y, (y_avg - adj_y / 2), y_avg, (y_avg + adj_y / 2), ub_y]
    yLabels = [np.round(lb_y,2), np.round((y_avg - adj_y / 2),2), np.round(y_avg,2), np.round((y_avg + adj_y / 2),2), np.round(ub_y,2)]

    # set y tick labels
    if ytick_labels:
        ax.set_yticks(yLabelValues)
        ax.set_yticklabels(yLabels)

    # plot remaining points and quadrant lines
    for result, color in zip(['W', 'L'], ['#002D62', '#FDBB30']):
        subset_data = data[data['result'] == result]
        ax.scatter(x=subset_data['x'], y=subset_data['y'], linewidth = 0.25, edgecolor='blue',c=color, zorder=99, s=15,label=result.upper())

    ax.axvline(x_avg, c='k', lw=1)
    ax.axhline(y_avg, c='k', lw=1)

    ax.scatter(x = leagueAvg, y = leagueAvg, s=10,c = 'black', label="League Average")
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

def generate_plot(nba_team, team_stat, opponent_stat):
    
    # Find the home team ID
    team_info = teams.find_teams_by_full_name(nba_team)
    team_id = team_info[0]['id']

    # Get all the games for the home team
    HomeTeamGameFinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    AllGames = HomeTeamGameFinder.get_data_frames()[0].dropna().set_index('GAME_ID')

    # HomeTeam WL
    WinLoss = AllGames['WL']

    # Only care about the selected stat
    AllGames = AllGames[stat_rename_dict[team_stat]]
    AllGames.name = home_team_stat_rename_dict.get(AllGames.name)

    # Fetch game logs for the opponents
    OpponentTeamGames = leaguegamefinder.LeagueGameFinder(vs_team_id_nullable = team_id)
    AllOpponentGames = OpponentTeamGames.get_data_frames()[0].dropna().set_index('GAME_ID')

    # Only care about the selected stat
    AllOpponentGames = AllOpponentGames[stat_rename_dict[opponent_stat]]
    AllOpponentGames.name = away_team_stat_rename_dict.get(AllOpponentGames.name)

    gameLogs = pd.merge(AllGames,AllOpponentGames, left_index=True, right_index=True)
    gameLogs = pd.merge(gameLogs, WinLoss,left_index=True, right_index=True)

    image = quadrant_chart(gameLogs[AllGames.name], gameLogs[AllOpponentGames.name], 
                result_labels = gameLogs['WL'])

    return image
