from flask import Flask, render_template, jsonify
from threading import Thread
import os
from get_gas_prices import get_gas_prices

app = Flask(__name__)

@app.route('/')
def home():
    # Helper request to get initial data (optional, or we can fetch in JS)
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    # For now, let's just get New York as default or extend to query params
    # We will fetch raw text from get_gas_prices but ideally we'd want structured JSON.
    # Parsing the text for the demo:
    raw_text = get_gas_prices("New York")
    
    # Simple parsing to extract price for display
    # Realistically we should refactor get_gas_prices to return a Dict, then format text.
    # But for now, we send the text to be displayed.
    return jsonify({"text": raw_text})

def run():
    # Use PORT env var if available (Clouds usage), else 5000
    port = int(os.environ.get("PORT", 5000))
    # Host 0.0.0.0 is important for cloud access
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
