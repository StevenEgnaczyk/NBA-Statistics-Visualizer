from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from scripts.nba_api import generate_plot
import os
import logging

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            logger.error("No JSON data received.")
            return jsonify(error="No JSON data received"), 400

        team = data.get('team')
        stat1 = data.get('stat1')
        stat2 = data.get('stat2')

        logger.info(f"Received data: team={team}, stat1={stat1}, stat2={stat2}")

        # Generate plot
        try:
            result = generate_plot(team, stat1, stat2)
            logger.info("Plot generated successfully.")
        except Exception as e:
            logger.error(f"Error generating plot: {e}")
            return jsonify(error="Error generating plot"), 500
        
        # Send the generated image
        return send_file(result, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return jsonify(error="An unexpected error occurred"), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))  # Use the environment variable for Render
    app.run(debug=True, port=port)
