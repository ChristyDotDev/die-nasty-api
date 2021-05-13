import schedule
import time
import os
import pendulum
from notifications.discord_sender import Discord
from sleeper_wrapper import League, Stats, Players
from notifications.constants import STARTING_MONTH, STARTING_YEAR, STARTING_DAY, START_DATE_STRING
from datetime import date
from notifications.injury_report import get_injury_report
from notifications.stonks import get_trade_leaders, get_trending_players

"""
These are all of the utility functions.
"""


def get_league_scoreboards(league_id, week):
    """
    Returns the scoreboards from the specified sleeper league.
    :param league_id: Int league_id
    :param week: Int week to get the scoreboards of
    :return: dictionary of the scoreboards; https://github.com/SwapnikKatkoori/sleeper-api-wrapper#get_scoreboards
    """
    league = League(league_id)
    matchups = league.get_matchups(week)
    users = league.get_users()
    rosters = league.get_rosters()
    scoreboards = league.get_scoreboards(rosters, matchups, users, "pts_half_ppr", week)
    return scoreboards


def make_roster_dict(starters_list, bench_list):
    """
    Takes in a teams starter list and bench list and makes a dictionary with positions.
    :param starters_list: List of a teams starters
    :param bench_list: List of a teams bench players
    :return: {starters:{position: []} , bench:{ position: []} }
    """
    week = get_current_week()
    players = Players().get_all_players()
    stats = Stats()
    week_stats = stats.get_week_stats("regular", STARTING_YEAR, week)

    roster_dict = {"starters": {}, "bench": {}}
    for player_id in starters_list:
        player = players[player_id]
        player_position = player["position"]
        player_name = player["first_name"] + " " + player["last_name"]
        try:
            player_std_score = week_stats[player_id]["pts_std"]
        except KeyError:
            player_std_score = None

        player_and_score_tup = (player_name, player_std_score)
        if player_position not in roster_dict["starters"]:
            roster_dict["starters"][player_position] = [player_and_score_tup]
        else:
            roster_dict["starters"][player_position].append(player_and_score_tup)

    for player_id in bench_list:
        player = players[player_id]
        player_position = player["position"]
        player_name = player["first_name"] + " " + player["last_name"]

        try:
            player_std_score = week_stats[player_id]["pts_std"]
        except KeyError:
            player_std_score = None

        player_and_score_tup = (player_name, player_std_score)
        if player_position not in roster_dict["bench"]:
            roster_dict["bench"][player_position] = [player_and_score_tup]
        else:
            roster_dict["bench"][player_position].append(player_and_score_tup)

    return roster_dict


def map_users_to_team_name(users):
    """
    Maps user_id to team_name
    :param users:  https://docs.sleeper.app/#getting-users-in-a-league
    :return: Dict {user_id:team_name}
    """
    users_dict = {}

    # Maps the user_id to team name for easy lookup
    for user in users:
        try:
            users_dict[user["user_id"]] = user["metadata"]["team_name"]
        except:
            users_dict[user["user_id"]] = user["display_name"]
    return users_dict


def map_roster_id_to_owner_id(league_id):
    """

    :return: Dict {roster_id: owner_id, ...}
    """
    league = League(league_id)
    rosters = league.get_rosters()
    result_dict = {}
    for roster in rosters:
        roster_id = roster["roster_id"]
        owner_id = roster["owner_id"]
        result_dict[roster_id] = owner_id

    return result_dict


def get_current_week():
    """
    Gets the current week.
    :return: Int current week
    """
    today = pendulum.today()
    starting_week = pendulum.datetime(STARTING_YEAR, STARTING_MONTH, STARTING_DAY)
    week = today.diff(starting_week).in_weeks()
    return week + 1