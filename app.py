from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/")
def hello():
    return jsonify({'league': os.getenv("LEAGUE_ID"),
                    'status': 'up'})


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
