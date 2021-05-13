from flask import Flask, jsonify
from sleeper_data.player_value import find_value
import os

app = Flask(__name__)


@app.route("/")
def hello():
    return jsonify({'league': os.getenv("LEAGUE_ID"),
                    'status': 'up'})


@app.route("/value/<player>")
def data(player):
    return jsonify({'value': find_value(player)})


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
