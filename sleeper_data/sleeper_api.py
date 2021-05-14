from sleeper_wrapper import Players
import functools


class SleeperApi:

    def __init__(self):
        print("initialised Sleeper API")

    @functools.cached_property
    def players(self):
        print("getting players from Sleeper")
        return Players().get_all_players()

    @functools.cached_property
    def players_simple(self):
        basic = {}
        for player in self.players:
            player_data = self.players[player]
            basic[player] = {
                "position": player_data.get("position"),
                "college": player_data.get("college"),
                "years_exp": player_data.get("years_exp"),
                "player_id": player_data.get("player_id"),
                "birth_date": player_data.get("birth_date"),
                "number": player_data.get("number"),
                "weight": player_data.get("weight"),
                "team": player_data.get("team"),
                "full_name": player_data.get("full_name"),
                "height": player_data.get("height"),
            }
        return basic
