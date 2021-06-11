from flask import Flask, jsonify, request
from sleeper_data.sleeper_api import SleeperApi
import os

app = Flask(__name__)
sleeper_api = SleeperApi(os.getenv("LEAGUE_ID"))


@app.route("/")
def hello():
    return jsonify({'league': os.getenv("LEAGUE_ID"),
                    'status': 'up'})


@app.route("/value/<player>")
def player_value(player):
    return jsonify({'value': find_value(player)})


@app.route('/player/', methods=['GET', 'POST'])
def get_players():
    if request.data:
        player_ids = request.get_json()['ids']
        filtered_players = {k: sleeper_api.players_simple[k] for k in player_ids}
        return jsonify(filtered_players)
    else:
        return jsonify(sleeper_api.players_simple)


@app.route('/league/trades', methods=['GET'])
def get_trades():
    trades = sleeper_api.get_trades()
    return jsonify(trades)


@app.route('/league/rosters', methods=['GET'])
def get_rosters():
    rosters = sleeper_api.get_rosters()
    return jsonify(rosters)


@app.route('/league/schedule', methods=['GET'])
def get_schedule():
    slate = sleeper_api.nfl_slate()
    fixtures = sleeper_api.schedule
    schedule = {
        "fixtures": fixtures,
        "currentWeek": slate['week']
    }
    return jsonify(schedule)


@app.route('/league/drafts', methods=['GET'])
def get_drafts():
    schedule = sleeper_api.get_drafts
    return jsonify(schedule)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
