from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from scripts.nba_api import generate_plot
import os

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

@app.route('/submit', methods=['POST'])
def submit():
    try:
        team = request.form.get('team')
        stat1 = request.form.get('stat1')
        stat2 = request.form.get('stat2')

        try:
            result = generate_plot(team, stat1, stat2)
        except Exception as e:
            print(e)
            return jsonify(error="Error generating plot"), 500
        
        return send_file(result, mimetype='image/png')
        
    except Exception as e:
        return 'Error'

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))  # Use the environment variable for Render
    app.run(debug=True, port=port)
