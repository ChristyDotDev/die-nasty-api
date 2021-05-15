from sleeper_wrapper import Players, League
import functools


class SleeperApi:

    def __init__(self, league_id):
        self.league_id = league_id
        league_api = League(league_id)
        league = league_api.get_league()
        self.current_week = league['settings']['leg']
        # previous_league = league['previous_league_id']
        self.rosters = league_api.get_rosters()
        self.users = league_api.get_users()
        self.transactions = []
        for week in range(0, self.current_week + 1):
            txns = league_api.get_transactions(week)
            for txn in txns:
                self.transactions.append(txn)
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

    @functools.cached_property
    def rostered_players(self):
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

    def get_trades(self):
        trades = [t for t in self.transactions if t['type'] == 'trade' and t['status'] == 'complete']

        trades_objs = []
        for trade in trades:
            for add in trade['adds']:
                new_roster = next((r for r in self.rosters if r['roster_id'] == trade['adds'][add]), None)
                new_owner = next((r for r in self.users if r['user_id'] == new_roster['owner_id']), None)
                print(new_owner['display_name'])
                print(self.players[add]['full_name'])
            trade_obj = {
                "timestamp": trade['status_updated'],
                "transaction_id": trade["transaction_id"],
                "adds": trade["adds"],
                "draft_picks": trade["draft_picks"]
            }
            trades_objs.append(trade_obj)
        return trades_objs
