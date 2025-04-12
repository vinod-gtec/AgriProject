from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import joblib

# Initialize Flask app with static and template folder
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "your_secret_key"
CORS(app)

# Load the trained model and encoders
# ------------------ Language Management ------------------

def get_language():
    return session.get('language', 'en')

@app.route('/set_language', methods=['POST'])
def set_language():
    data = request.get_json()
    lang = data.get('language', 'en')
    session['language'] = lang
    return jsonify({'message': 'Language set successfully', 'language': lang})

# ------------------ Web Page Routes ------------------

@app.route('/')
def home():
    return render_template('index.html', language=get_language())

@app.route('/soiltesting')
def soiltesting():
    return render_template('soiltesting.html', language=get_language())

@app.route('/harvest')
def harvest():
    return render_template('harvest.html', language=get_language())

@app.route('/pest')
def pest():
    return render_template('pest.html', language=get_language())

@app.route('/cropmanagement')
def crop_management():
    return render_template('cropmanagement.html', language=get_language())

@app.route('/irrigation')
def irrigation():
    return render_template('irrigation.html', language=get_language())

@app.route('/schemes')
def schemes():
    return render_template('schemes.html', language=get_language())

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', language=get_language())

#---------------------------------------------------------Irrigation Prediction---------------------------------------------------------
from flask import request, jsonify
from geopy.distance import geodesic
import googlemaps

# Ensure gmaps is initialized once globally
API_KEY = "AIzaSyCNXTabHH8WPHwcEUBkTQaNtS5N5iCdtUU"
gmaps = googlemaps.Client(key=API_KEY)

def get_nearest_water_source(user_location):
    places = gmaps.places_nearby(
        location=user_location,
        radius=8000,
        keyword="water body OR lake OR river OR reservoir OR pond",
        type="natural_feature"
    )

    if not places['results']:
        return None

    nearest_source = min(
        places['results'],
        key=lambda place: geodesic(user_location, (
            place['geometry']['location']['lat'], 
            place['geometry']['location']['lng']
        )).km
    )

    return {
        "name": nearest_source.get("name", "Unknown"),
        "lat": nearest_source['geometry']['location']['lat'],
        "lng": nearest_source['geometry']['location']['lng'],
        "distance_km": round(geodesic(user_location, (
            nearest_source['geometry']['location']['lat'], 
            nearest_source['geometry']['location']['lng']
        )).km, 2)
    }

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    location_text = data.get('location')

    # Geocode the user-entered location
    geocode_result = gmaps.geocode(location_text)
    if not geocode_result:
        return jsonify({"error": "Invalid location"}), 400

    latlng = geocode_result[0]['geometry']['location']
    user_location = (latlng['lat'], latlng['lng'])

    result = get_nearest_water_source(user_location)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No water sources found nearby."}), 404



# ------------------ Run Server ------------------

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
