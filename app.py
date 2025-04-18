from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import joblib
import numpy as np

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
API_KEY = "AIzaSyCNXTabHH8WPHwcEUBkTQaNtS5N5iCdtUU "
gmaps = googlemaps.Client(key=API_KEY)

def get_nearest_water_source(user_location):
    places = gmaps.places_nearby(
        location=user_location,
        radius=8000,
        keyword="water body OR lake OR river OR reservoir OR pond OR water source ",
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

#--------------------------harvtest------------------------------------------------------------------------
database_of_farmers = [
    {
        "farmer_id": 1,
        "name": "Ramesh",
        "land_size": 1.5,
        "organic": True,
        "soil_card": False,
        "crop": "Wheat",
        "kcc_holder": False,
        "category": "General",
        "annual_income": 70000
    },
    {
        "farmer_id": 2,
        "name": "Sita",
        "land_size": 3.0,
        "organic": False,
        "soil_card": True,
        "crop": "Paddy",
        "kcc_holder": True,
        "category": "SC",
        "annual_income": 95000
    },
    {
        "farmer_id": 3,
        "name": "Vinod kumar",
        "land_size": 1.0,
        "organic": True,
        "soil_card": False,
        "crop": "Rice",
        "kcc_holder": False,
        "category": "General",
        "annual_income": 30000
    }
]

# Scheme definitions
scheme_definitions = [
    {
        "name": "PM-KISAN",
        "required_params": ["land_size"],
        "eligibility": lambda f: f.get("land_size", 0) <= 2
    },
    {
        "name": "Organic Farming Support",
        "required_params": ["organic"],
        "eligibility": lambda f: f.get("organic") is True
    },
    {
        "name": "Soil Health Scheme",
        "required_params": ["soil_card"],
        "eligibility": lambda f: f.get("soil_card") is False
    },
    {
        "name": "KCC Scheme",
        "required_params": ["kcc_holder"],
        "eligibility": lambda f: f.get("kcc_holder") is False
    },
    {
        "name": "Rainfed Agriculture Assistance Scheme",
        "required_params": ["land_size", "soil_card"],
        "eligibility": lambda f: f.get("land_size", 0) <= 2 and f.get("soil_card") is False
    }
]

def check_eligibility(farmer, scheme):
    missing = [p for p in scheme["required_params"] if p not in farmer]
    if missing:
        return {"scheme": scheme["name"], "eligible": False, "reason": f"Missing: {', '.join(missing)}"}
    eligible = scheme["eligibility"](farmer)
    return {
        "scheme": scheme["name"],
        "eligible": eligible,
        "reason": "Eligible" if eligible else "Does not meet criteria"
    }

def recommend_schemes(farmer, schemes):
    return [check_eligibility(farmer, s) for s in schemes]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_eligibility', methods=['POST'])
def check():
    data = request.json
    name = data.get("name", "").strip().lower()
    farmer = next((f for f in database_of_farmers if f["name"].lower() == name), None)
    if not farmer:
        return jsonify([{"scheme": "All", "eligible": False, "reason": "Farmer not found"}])
    return jsonify(recommend_schemes(farmer, scheme_definitions))
#-----------------------------------------------------------------------------------------------------------
#----------------------------Get nearby Soil testing Lab----------------------------------------------------

import requests


GOOGLE_API_KEY = 'AIzaSyCNXTabHH8WPHwcEUBkTQaNtS5N5iCdtUU'  # Replace with your valid key

def get_nearby_soil_testing_labs(api_key, latitude, longitude, radius=10000):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{latitude},{longitude}',
        'radius': radius,
        'keyword': 'soil testing lab',
        'key': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    labs_list = []
    if data.get('status') == 'OK':
        for lab in data['results']:
            name = lab.get('name')
            address = lab.get('vicinity')
            labs_list.append({'name': name, 'address': address})
    return labs_list

@app.route('/get-labs', methods=['POST'])
def get_labs():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    labs = get_nearby_soil_testing_labs(GOOGLE_API_KEY, latitude, longitude)
    return jsonify({'labs': labs})

#-----------------------------------------------------------------------------------------------------------
N=33
P=45
K=13
T=35
H=13
PH=18
R=13
#-------------------------------Crop Prediction----------------------------------------------------
# in an older environment
import tensorflow as tf
from keras.models import load_model, save_model


model = load_model("crop_LSTM.h5")
save_model(model, "crop_LSTM_converted.h5")


Crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
         'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
         'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
         'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']

sc_mean = np.array([50.3926, 52.8823, 47.2357, 25.5861, 71.2023, 6.4606, 104.995])
sc_std = np.array([36.6511, 32.5009, 49.1960, 5.0861, 22.5062, 0.7817, 55.6628])

def scale(x):
    return (x - sc_mean) / sc_std

@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    recommended_crop = None
    data = [float(request.form[i]) for i in ['N', 'P', 'K', 'T', 'H', 'PH', 'R']]
    scaled = scale(np.array([data]))
    pred = np.argmax(model.predict(scaled))
    recommended_crop = Crops[pred]
    return render_template('cropmanagement.html', result=recommended_crop, language=get_language())


if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True,port=5002)
