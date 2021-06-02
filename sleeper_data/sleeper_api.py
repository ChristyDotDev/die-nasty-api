import functools

from sleeper_wrapper import Players, League


class SleeperApi:
    POSITIONS = ["QB", "RB", "WR", "TE"]

    def ordinal(self, n):
        n = int(n)
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix

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

        past_leagues = []
        past_leagues.append(league['previous_league_id'])
        while past_leagues:
            past_league_id = past_leagues.pop()
            past_league_api = League(past_league_id)
            past_league_info = past_league_api.get_league()
            if 'previous_league_id' in past_league_info and int(past_league_info['previous_league_id']) > 0:
                past_leagues.append(past_league_info['previous_league_id'])
            for week in range(0, 17):
                txns = past_league_api.get_transactions(week)
                for txn in txns:
                    self.transactions.append(txn)
            # get rosters and add to list. Or do roster IDs stay the same through the years
        self.transactions.sort(key=lambda k: k['status_updated'], reverse=True)
        print('finished')
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
                "avatar_url": f'https://sleepercdn.com/content/nfl/players/{player_data.get("player_id")}.jpg',
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
            trade_parts = {}
            for tr in trade['roster_ids']:
                new_roster = next((r for r in self.rosters if r['roster_id'] == tr), None)
                new_owner = next((r for r in self.users if r['user_id'] == new_roster['owner_id']), None)
                trade_parts[tr] = {
                    "newRoster": new_owner['display_name'],
                    "adds": [],
                }
            if 'adds' in trade and trade['adds'] is not None:
                for add in trade['adds']:
                    new_roster = trade['adds'][add]
                    trade_parts[new_roster]['adds'].append(self.players[add]['full_name'])
            if 'draft_picks' in trade and trade['draft_picks'] is not None:
                for pick in trade['draft_picks']:
                    trade_parts[pick['owner_id']]['adds'].append(f"{pick['season']} {self.ordinal(pick['round'])}")

            adds = [trade_parts[x] for x in trade_parts]
            trade_obj = {
                "timestamp": trade['status_updated'],
                "transaction_id": trade["transaction_id"],
                "trade_parts": adds,
            }
            trades_objs.append(trade_obj)
        return trades_objs

    def get_rosters(self):
        print(self.rosters)
        rosters_list = []
        for roster in self.rosters:
            players = [self.players_simple[player_id] for player_id in roster.get("players")]
            players.sort(key=lambda p: self.POSITIONS.index(p.get("position")))
            rosters_list.append({
                "player_ids": roster.get("players"),
                "taxi": roster.get("taxi"),
                "starters": roster.get("starters"),
                "owner_id": roster.get("owner_id"),
                "players": players
            })
        return rosters_list

    def get_schedule(self):
        league_api = League(self.league_id)
        schedule = league_api.get_matchups(1)
        schedule_obj = {}
        matchup_ids = [x['matchup_id'] for x in schedule]
        for m in matchup_ids:
            schedule_obj[m] = []
        #print(schedule)
        for team in schedule:
            print(team)
            roster = next((r for r in self.rosters if r['roster_id'] == team['roster_id']), None)
            user = next((r for r in self.users if r['user_id'] == roster['owner_id']), None)
            team_name = user['metadata'].get('team_name', user['display_name'])
            schedule_obj[team['matchup_id']].append({
                "team": team_name,
                "avatar": f"https://sleepercdn.com/avatars/thumbs/{user['avatar']}"
            })
            print(user)
        return schedule_obj
