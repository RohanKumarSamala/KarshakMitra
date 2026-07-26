import os, json, io, threading

# Keras must be told which backend to use *before* it is imported. The model is a
# Keras 3 file, so any Keras 3 backend can run it -- we default to JAX because
# TensorFlow has no wheels for Python 3.14 (that is why inference used to be
# mocked out). Override with KERAS_BACKEND=tensorflow if you have TF installed.
os.environ.setdefault("KERAS_BACKEND", "jax")

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import numpy as np
import keras

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'universal_plant_model.h5'
CLASSES_PATH = 'universal_class_names.json'
INPUT_SIZE = (224, 224)

model = None
class_names = []
load_error = None
# Keras predict calls are not guaranteed thread-safe, and gunicorn/Flask may
# serve concurrent requests, so serialise inference.
predict_lock = threading.Lock()

try:
    model = keras.saving.load_model(MODEL_PATH, compile=False)
    with open(CLASSES_PATH, 'r') as f:
        class_names = json.load(f)

    if model.output_shape[-1] != len(class_names):
        raise ValueError(
            f"Model outputs {model.output_shape[-1]} classes but "
            f"{CLASSES_PATH} lists {len(class_names)}"
        )

    # First inference pays the JAX trace/compile cost, so absorb it at startup
    # instead of making the first farmer wait for it.
    model.predict(np.zeros((1, *INPUT_SIZE, 3), dtype='float32'), verbose=0)
    print(f"Model loaded on '{keras.backend.backend()}' backend: "
          f"{len(class_names)} classes, input {model.input_shape}")
except Exception as e:
    load_error = str(e)
    print(f"CRITICAL ERROR: Failed to load model or class names. Error: {e}")

knowledge_base = {
    "Potato___Early_blight": { "description": "A fungal disease causing dark lesions, often in a 'target' pattern.", "prevention": "Ensure good air circulation; avoid overhead watering; rotate crops.", "treatment": "Apply copper-based or chlorothalonil fungicides." },
    "Tomato___Late_blight": { "description": "A destructive water mold disease causing large, dark blotches on leaves and stems.", "prevention": "Use resistant varieties; ensure good drainage; apply preventative fungicides.", "treatment": "Use fungicides with mancozeb, metalaxyl, or propamocarb." },
    "Corn_(maize)___Common_rust_": { "description": "Characterized by reddish-brown pustules on both sides of the leaves.", "prevention": "Plant resistant hybrids; manage crop residue.", "treatment": "Fungicide application is typically only for sweet corn or seed production." },
    "Apple___Apple_scab": { "description": "A fungal disease causing olive-green to brown spots on leaves, fruit, and twigs.", "prevention": "Prune trees for better air flow; clean up fallen leaves in autumn.", "treatment": "Apply fungicides like captan or sulfur from bud break until dry weather." },
    "Tomato___healthy": { "description": "The plant appears healthy.", "prevention": "Maintain consistent watering, good nutrition, and monitor regularly.", "treatment": "No treatment necessary." },
    "Potato___healthy": { "description": "The plant appears healthy.", "prevention": "Use certified seed potatoes and ensure well-drained soil.", "treatment": "No treatment necessary." }
}


def preprocess_image(image, target_size=INPUT_SIZE):
    """Prepare a PIL image for the model.

    The saved EfficientNet keeps its Rescaling and Normalization layers inside
    the graph, so it expects raw 0-255 pixel values. Do NOT divide by 255 here
    or the input gets scaled twice and predictions collapse toward noise.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size, Image.LANCZOS)
    array = np.asarray(image, dtype='float32')
    return np.expand_dims(array, axis=0)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': f'Model unavailable: {load_error}'}), 503
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'}), 400
    try:
        image = Image.open(io.BytesIO(file.read()))
        processed_image = preprocess_image(image)

        with predict_lock:
            prediction = np.asarray(model.predict(processed_image, verbose=0))[0]

        predicted_index = int(np.argmax(prediction))
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


if __name__ == '__main__':
    # debug=True reloads the process on save, which reloads the 65 MB model too.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
