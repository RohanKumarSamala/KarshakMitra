import os, json, io, requests
from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'universal_plant_model.h5'
CLASSES_PATH = 'universal_class_names.json'
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")  # Set this in Render dashboard / .env

try:
    model = load_model(MODEL_PATH)
    with open(CLASSES_PATH, 'r') as f:
        class_names = json.load(f)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load model or class names. Check file paths. Error: {e}")

knowledge_base = {
    "Potato___Early_blight": { "description": "A fungal disease causing dark lesions, often in a 'target' pattern.", "prevention": "Ensure good air circulation; avoid overhead watering; rotate crops.", "treatment": "Apply copper-based or chlorothalonil fungicides." },
    "Tomato___Late_blight": { "description": "A destructive water mold disease causing large, dark blotches on leaves and stems.", "prevention": "Use resistant varieties; ensure good drainage; apply preventative fungicides.", "treatment": "Use fungicides with mancozeb, metalaxyl, or propamocarb." },
    "Corn_(maize)___Common_rust_": { "description": "Characterized by reddish-brown pustules on both sides of the leaves.", "prevention": "Plant resistant hybrids; manage crop residue.", "treatment": "Fungicide application is typically only for sweet corn or seed production." },
    "Apple___Apple_scab": { "description": "A fungal disease causing olive-green to brown spots on leaves, fruit, and twigs.", "prevention": "Prune trees for better air flow; clean up fallen leaves in autumn.", "treatment": "Apply fungicides like captan or sulfur from bud break until dry weather." },
    "Tomato___healthy": { "description": "The plant appears healthy.", "prevention": "Maintain consistent watering, good nutrition, and monitor regularly.", "treatment": "No treatment necessary." },
    "Potato___healthy": { "description": "The plant appears healthy.", "prevention": "Use certified seed potatoes and ensure well-drained soil.", "treatment": "No treatment necessary." }
}

def preprocess_image(image, target_size=(224, 224)):
    if image.mode != "RGB": image = image.convert("RGB")
    image = image.resize(target_size)
    image = np.asarray(image)
    image = np.expand_dims(image, axis=0)
    image = image / 255.0
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'}), 400
    try:
        image = Image.open(io.BytesIO(file.read()))
        processed_image = preprocess_image(image)
        prediction = model.predict(processed_image)[0]

        predicted_index = np.argmax(prediction)
        predicted_class_key = class_names[predicted_index]
        confidence = float(prediction[predicted_index])

        crop_name = predicted_class_key.split('___')[0].replace('_', ' ').replace('(maize)', 'Maize')
        disease_name = predicted_class_key.split('___')[1].replace('_', ' ') if '___' in predicted_class_key else 'Healthy'

        info = knowledge_base.get(predicted_class_key, {
            "description": "Details for this disease are not yet available in our database.",
            "prevention": "General advice: Ensure proper watering, sunlight, and soil nutrients.",
            "treatment": "Consult a local agricultural expert for specific advice."
        })

        return jsonify({
            'crop': crop_name, 'disease': disease_name, 'confidence': confidence,
            'description': info['description'], 'prevention': info['prevention'], 'treatment': info['treatment']
        })
    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({'error': 'Failed to process the image.'}), 500

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.json
    lat, lon = data.get('lat'), data.get('lon')
    if not lat or not lon: return jsonify({'error': 'Missing location data'}), 400
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
    try:
        response = requests.get(url)
        weather_data = response.json()
        temp, humidity = weather_data['main']['temp'], weather_data['main']['humidity']
        risk = "Low"
        if temp > 20 and humidity > 75: risk = "High risk for fungal diseases"
        elif temp > 18 and humidity > 60: risk = "Moderate risk for fungal diseases"
        return jsonify({ 'temperature': temp, 'humidity': humidity, 'risk': risk })
    except Exception as e:
        print(f"Weather API Error: {e}")
        return jsonify({'error': 'Could not fetch weather data.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)