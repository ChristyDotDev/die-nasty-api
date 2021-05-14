from flask import Flask, jsonify, request
from sleeper_data.player_value import find_value
from sleeper_data.sleeper_api import SleeperApi
import os

app = Flask(__name__)
sleeper_api = SleeperApi()


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


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
