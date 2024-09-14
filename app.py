from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
from scripts.nba_api import generate_plot

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins. You can restrict this to specific origins.

@app.route('/submit', methods=['POST'])
def submit():
    try:
        team = request.json.get('team')
        stat1 = request.json.get('stat1')
        stat2 = request.json.get('stat2')

        logging.info(f"Received data - Team: {team}, Stat1: {stat1}, Stat2: {stat2}")

        try:
            result = generate_plot(team, stat1, stat2)
        except Exception as e:
            logging.error(f"Error generating plot: {e}")
            return jsonify(error="Error generating plot"), 500

        return send_file(result, mimetype='image/png')

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify(error="Error processing request"), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))  # Use the environment variable for Render
    app.run(debug=True, port=port)
