from flask import Flask, render_template, jsonify, request, send_from_directory
from threading import Thread
import os
from dotenv import load_dotenv
from get_gas_prices import get_gas_prices
import places

load_dotenv()
app = Flask(__name__)
# Pick up edits to templates/index.html without restarting
app.config["TEMPLATES_AUTO_RELOAD"] = True

def firebase_config():
    # Login is optional: only turned on once the Firebase settings are in the environment
    if not os.getenv("FIREBASE_API_KEY"):
        return None
    project = os.getenv("FIREBASE_PROJECT_ID", "")
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", f"{project}.firebaseapp.com"),
        "projectId": project,
        "appId": os.getenv("FIREBASE_APP_ID", ""),
    }

@app.route('/')
def home():
    return render_template('index.html', firebase_config=firebase_config())

# The service worker has to be served from the root so it covers the whole app
@app.route('/sw.js')
def service_worker():
    rsp = send_from_directory(app.static_folder, 'sw.js', mimetype='application/javascript')
    rsp.headers['Cache-Control'] = 'no-cache'
    return rsp

@app.route('/manifest.webmanifest')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.webmanifest', mimetype='application/manifest+json')

@app.route('/api/data')
def api_data():
    # State average (CollectAPI), kept for the original dashboard
    raw_text = get_gas_prices("New York")
    return jsonify({"text": raw_text})

@app.route('/api/nearby')
def api_nearby():
    # Station-by-station prices around the phone's location
    try:
        lat = float(request.args["lat"])
        lng = float(request.args["lng"])
    except (KeyError, ValueError):
        return jsonify({"error": "lat and lng are required"}), 400
    try:
        return jsonify({"stations": places.stations_near(lat, lng)})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502

@app.route('/api/search')
def api_search():
    # Same thing but for a typed zip code / town
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q is required"}), 400
    try:
        return jsonify({"stations": places.stations_for_place(query)})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502

def run():
    # Use PORT env var if available (Clouds usage), else 5000
    port = int(os.environ.get("PORT", 5000))
    # Host 0.0.0.0 is important for cloud access
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    # Run just the web app without the Discord bot
    run()
