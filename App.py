from flask import Flask, request, jsonify, send_from_directory, send_file, render_template
from flask_cors import CORS
from static.scripts.nba_api import generate_plot
import os


app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/projects/nba-api.html')
def nba_api():
    return send_from_directory('projects', 'nba-api.html')

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
        
        return send_file(result, mimetype='image/png')
        
    except Exception as e:
        return jsonify(error=str(e)), 500

def your_function(team, stat1, stat2):
    return f"Received team: {team}, stat1: {stat1}, stat2: {stat2}"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
