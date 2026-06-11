import os, json, io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'universal_plant_model.h5'
CLASSES_PATH = 'universal_class_names.json'

# --- MOCKED FOR DEMONSTRATION ---
# TensorFlow is disabled so you can run the UI on Python 3.14
class_names = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_", 
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___healthy"
]
knowledge_base = {
    "Potato___Early_blight": { "description": "A fungal disease causing dark lesions, often in a 'target' pattern.", "prevention": "Ensure good air circulation; avoid overhead watering; rotate crops.", "treatment": "Apply copper-based or chlorothalonil fungicides." },
    "Tomato___Late_blight": { "description": "A destructive water mold disease causing large, dark blotches on leaves and stems.", "prevention": "Use resistant varieties; ensure good drainage; apply preventative fungicides.", "treatment": "Use fungicides with mancozeb, metalaxyl, or propamocarb." },
    "Corn_(maize)___Common_rust_": { "description": "Characterized by reddish-brown pustules on both sides of the leaves.", "prevention": "Plant resistant hybrids; manage crop residue.", "treatment": "Fungicide application is typically only for sweet corn or seed production." },
    "Apple___Apple_scab": { "description": "A fungal disease causing olive-green to brown spots on leaves, fruit, and twigs.", "prevention": "Prune trees for better air flow; clean up fallen leaves in autumn.", "treatment": "Apply fungicides like captan or sulfur from bud break until dry weather." },
    "Tomato___healthy": { "description": "The plant appears healthy.", "prevention": "Maintain consistent watering, good nutrition, and monitor regularly.", "treatment": "No treatment necessary." },
    "Potato___healthy": { "description": "The plant appears healthy.", "prevention": "Use certified seed potatoes and ensure well-drained soil.", "treatment": "No treatment necessary." }
}

def preprocess_image(image, target_size=(224, 224)):
    # Mocked preprocess
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'}), 400
    try:
        # File is received but we don't need to process it for the mock
        pass
        # --- MOCKED PREDICTION ---
        import random
        predicted_class_key = random.choice(["Tomato___Late_blight", "Potato___healthy", "Apple___Apple_scab"])
        confidence = round(random.uniform(0.85, 0.99), 2)

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)