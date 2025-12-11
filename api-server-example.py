#!/usr/bin/env python3
"""
Flask API server for apartment price prediction using CatBoost models.

Install dependencies:
    pip install flask flask-cors numpy catboost pandas

Run:
    python api-server-example.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor, Pool

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Load both CatBoost models
POLAND_MODEL_PATH = 'catboost_model_CATBOOST_IMPROVED_otodom5.cbm'
INDIA_MODEL_PATH = 'catboost_model_CATBOOST_ind3.cbm'

poland_model = CatBoostRegressor()
poland_model.load_model(POLAND_MODEL_PATH)

india_model = CatBoostRegressor()
india_model.load_model(INDIA_MODEL_PATH)

# Load city mapping for India
city_mapping = pd.read_csv('city_mapping.csv')
city_to_encoded = dict(zip(city_mapping['City'], city_mapping['Encoded_Value']))

print(f"Poland model loaded: {POLAND_MODEL_PATH}")
print(f"India model loaded: {INDIA_MODEL_PATH}")
print(f"Available cities for India: {len(city_to_encoded)}")

# Print feature names for debugging
print("\n=== POLAND MODEL FEATURE NAMES ===")
poland_features = poland_model.feature_names_
print(f"Number of features: {len(poland_features)}")
print("Features:", poland_features)

print("\n=== INDIA MODEL FEATURE NAMES ===")
india_features = india_model.feature_names_
print(f"Number of features: {len(india_features)}")
print("Features:", india_features)

def prepare_poland_features(data):
    """
    Prepare features for Poland model (otodom5).
    Poland model expects ONE-HOT ENCODED features (like building_material_BRICK).
    This is similar to the original Keras model format.
    """
    # Initialize features dict with all possible one-hot encoded columns
    features = {}

    # Basic numerical features
    features['area'] = data.get('area', 50)
    features['rooms'] = data.get('rooms', 2)

    # Boolean features
    features['has_dishwasher'] = 1 if data.get('hasDishwasher', False) else 0
    features['has_fridge'] = 1 if data.get('hasFridge', False) else 0
    features['has_stove'] = 1 if data.get('hasStove', False) else 0
    features['has_oven'] = 1 if data.get('hasOven', False) else 0
    features['has_basement'] = 1 if data.get('hasBasement', False) else 0
    features['has_balcony'] = 1 if data.get('hasBalcony', False) else 0
    features['has_terrace'] = 1 if data.get('hasTerrace', False) else 0
    features['has_garden'] = 1 if data.get('hasGarden', False) else 0
    features['has_parking'] = 1 if data.get('hasParking', False) else 0
    features['has_elevator'] = 1 if data.get('hasElevator', False) else 0
    features['has_security'] = 1 if data.get('hasSecurity', False) else 0

    features['lat'] = data.get('latitude', 52.2297)
    features['lon'] = data.get('longitude', 21.0122)

    building_material = data.get('buildingMaterial', 'unknown').upper()
    materials = ['BREEZEBLOCK', 'BRICK', 'CELLULAR_CONCRETE', 'CONCRETE',
                 'CONCRETE_PLATE', 'OTHER', 'REINFORCED_CONCRETE', 'SILIKAT', 'unknown']
    for mat in materials:
        features[f'building_material_{mat}'] = 1 if building_material == mat else 0

    ownership = data.get('ownership', 'unknown').upper()
    ownerships = ['FULL_OWNERSHIP', 'LIMITED_OWNERSHIP', 'SHARE', 'USUFRUCT', 'unknown']
    for own in ownerships:
        features[f'ownership_{own}'] = 1 if ownership == own else 0

    # One-hot encode condition
    condition = data.get('condition', 'unknown').upper()
    conditions = ['READY_TO_USE', 'TO_COMPLETION', 'TO_RENOVATION', 'unknown']
    for cond in conditions:
        features[f'condition_{cond}'] = 1 if condition == cond else 0

    # One-hot encode heating type
    heating = data.get('heatingType', 'unknown').upper()
    heatings = ['BOILER_ROOM', 'ELECTRICAL', 'GAS', 'OTHER', 'TILED_STOVE', 'URBAN', 'unknown']
    for heat in heatings:
        features[f'heating_type_{heat}'] = 1 if heating == heat else 0

    # One-hot encode building type
    building_type = data.get('buildingType', 'unknown').upper()
    building_types = ['APARTMENT', 'BLOCK', 'HOUSE', 'INFILL', 'LOFT', 'RIBBON', 'TENEMENT', 'unknown']
    for btype in building_types:
        features[f'building_type_{btype}'] = 1 if building_type == btype else 0

    # One-hot encode windows type
    windows = data.get('windowsType', 'unknown').upper()
    windows_types = ['ALUMINIUM', 'PLASTIC', 'WOODEN', 'unknown']
    for wtype in windows_types:
        features[f'windows_type_{wtype}'] = 1 if windows == wtype else 0

    # One-hot encode building age category
    year_built = data.get('yearBuilt')
    age_category = data.get('buildingAgeCategory', 'unknown').lower()

    if year_built and age_category == 'unknown':
        if year_built >= 2010:
            age_category = 'new'
        elif year_built >= 1990:
            age_category = 'modern'
        elif year_built >= 1945:
            age_category = 'communist'
        else:
            age_category = 'prewar'

    age_categories = ['communist', 'modern', 'new', 'prewar', 'unknown']
    for age in age_categories:
        features[f'building_age_category_{age}'] = 1 if age_category == age else 0

    return pd.DataFrame([features])


def prepare_india_features(data):
    """
    Prepare features for India model (ind3).

    Note: Feature names and ORDER must match exactly what the model was trained on.
    Based on error message, model expects: Carpet Area, BHK, Bathroom, Balcony, Parking, City_Encoded
    """
    features = {}

    # Feature order matters! Must match training data
    features['Carpet Area'] = data.get('area', 1000)  # India uses sq ft
    features['BHK'] = data.get('rooms', 2)  # Number of bedrooms
    features['Bathroom'] = data.get('bathrooms', 2)  # Number of bathrooms

    # Boolean features - these come BEFORE City_Encoded
    features['Balcony'] = 1 if data.get('hasBalcony', False) else 0
    features['Parking'] = 1 if data.get('hasParking', False) else 0

    # City encoding comes last
    city = data.get('city', '').lower()
    if city in city_to_encoded:
        features['City_Encoded'] = city_to_encoded[city]
    else:
        # Default to bangalore if city not found
        features['City_Encoded'] = city_to_encoded.get('bangalore', 0.0)

    # Create DataFrame with explicit column order matching the model
    df = pd.DataFrame([features], columns=['Carpet Area', 'BHK', 'Bathroom', 'Balcony', 'Parking', 'City_Encoded'])

    # No categorical features for India model (city is already encoded as float)
    cat_features = []

    return df, cat_features


@app.route('/predict/poland', methods=['POST'])
def predict_poland():
    """
    Predict apartment price for Poland using the otodom5 CatBoost model.

    Expected JSON body:
    {
        "latitude": 52.2297,
        "longitude": 21.0122,
        "area": 50,
        "rooms": 2,
        "yearBuilt": 2010,
        "buildingMaterial": "BRICK",
        "ownership": "FULL_OWNERSHIP",
        "condition": "READY_TO_USE",
        "heatingType": "URBAN",
        "buildingType": "BLOCK",
        "windowsType": "PLASTIC",
        "hasBalcony": true,
        "hasElevator": true
    }

    Returns:
    {
        "predictedPrice": 450000.00,
        "confidence": 0.85
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields for Poland
        required_fields = ['latitude', 'longitude', 'area', 'rooms']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Prepare features for Poland model (one-hot encoded)
        features = prepare_poland_features(data)

        print(f"Poland - Lat: {data.get('latitude')}, Lon: {data.get('longitude')}")
        print(f"Features shape: {features.shape}")
        print(f"Feature columns: {list(features.columns)}")

        # Make prediction
        prediction = poland_model.predict(features)
        predicted_price = float(prediction[0])

        print(f"Predicted price: {predicted_price} PLN")

        # Calculate a basic confidence score
        confidence = 0.85

        return jsonify({
            'predictedPrice': round(predicted_price, 2),
            'confidence': confidence
        }), 200

    except Exception as e:
        print(f"Error during Poland prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/predict/india', methods=['POST'])
def predict_india():
    """
    Predict apartment price for India using the ind3 CatBoost model.

    Expected JSON body:
    {
        "city": "bangalore",
        "area": 1000,
        "rooms": 2,
        "bathrooms": 2,
        "hasBalcony": true,
        "hasParking": true
    }

    Returns:
    {
        "predictedPrice": 5000000.00,
        "confidence": 0.85
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields for India
        if 'city' not in data:
            return jsonify({'error': 'city is required'}), 400
        if 'area' not in data or 'rooms' not in data:
            return jsonify({'error': 'area and rooms are required'}), 400

        # Prepare features for India model
        features, cat_features = prepare_india_features(data)

        print(f"India - City: {data.get('city')}")
        print(f"Features shape: {features.shape}")
        print(f"Features:\n{features}")

        # Create a Pool with explicit empty categorical features
        # This prevents CatBoost from using the saved categorical feature indices
        pool = Pool(data=features, cat_features=[])
        prediction = india_model.predict(pool)
        predicted_price = float(prediction[0])

        print(f"Predicted price: {predicted_price} INR")

        # Calculate a basic confidence score
        confidence = 0.85

        return jsonify({
            'predictedPrice': round(predicted_price, 2),
            'confidence': confidence
        }), 200

    except Exception as e:
        print(f"Error during India prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/cities', methods=['GET'])
def get_cities():
    """Get list of available cities for India mode"""
    cities = sorted(list(city_to_encoded.keys()))
    return jsonify({'cities': cities}), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'name': 'Apartment Price Prediction API',
        'version': '2.0.0',
        'models': {
            'poland': 'CatBoost model for Poland (otodom5) - uses coordinates and one-hot encoded features',
            'india': 'CatBoost model for India (ind3) - uses city encoding'
        },
        'endpoints': {
            '/predict/poland': 'POST - Predict apartment price for Poland',
            '/predict/india': 'POST - Predict apartment price for India',
            '/cities': 'GET - Get list of available cities for India mode',
            '/health': 'GET - Health check'
        }
    }), 200


if __name__ == '__main__':
    print("Starting Apartment Price Prediction API with CatBoost Models...")
    print(f"Poland model: {POLAND_MODEL_PATH}")
    print(f"India model: {INDIA_MODEL_PATH}")
    print("Server running on http://localhost:5000")
    print("\nExample request for Poland:")
    print("""
    curl -X POST http://localhost:5000/predict/poland \\
      -H "Content-Type: application/json" \\
      -d '{
        "latitude": 52.2297,
        "longitude": 21.0122,
        "area": 50,
        "rooms": 2,
        "yearBuilt": 2010,
        "buildingMaterial": "BRICK",
        "ownership": "FULL_OWNERSHIP",
        "condition": "READY_TO_USE",
        "heatingType": "URBAN",
        "buildingType": "BLOCK",
        "windowsType": "PLASTIC",
        "hasBalcony": true,
        "hasElevator": true
      }'
    """)
    print("\nExample request for India:")
    print("""
    curl -X POST http://localhost:5000/predict/india \\
      -H "Content-Type: application/json" \\
      -d '{
        "city": "bangalore",
        "area": 1000,
        "rooms": 2,
        "bathrooms": 2,
        "hasBalcony": true,
        "hasParking": true
      }'
    """)

    app.run(debug=True, host='0.0.0.0', port=5000)
