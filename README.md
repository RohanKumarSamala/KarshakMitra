# KarshakMitra Pro — AI Crop Disease Detection

**KarshakMitra Pro** is an AI-powered smart farming companion designed to help farmers instantly detect crop diseases from photos. It provides real-time disease detection, prevention guidelines, and expert treatment advice in multiple languages.

---

## 🌟 Key Features

*   **Instant AI Diagnosis**: Scan crop leaves via live camera or upload images from the gallery.
*   **Multilingual Support**: Available in English, Hindi (हिन्दी), and Telugu (తెలుగు) to assist farmers across regions.
*   **Actionable Advice**: Detailed explanations, prevention steps, and treatment instructions for detected conditions.
*   **Offline-Ready Web Shell**: Designed with a responsive, premium mobile-first interface (glassmorphism design) suitable for mobile browsers.
*   **Scan History**: Local history storage to keep track of the last 5 crop scans.

---

## 🛠️ Tech Stack

*   **Frontend**: Vanilla HTML5, CSS3 (Modern Glassmorphism UI, Inter font), and ES6+ JavaScript.
*   **Backend**: Flask (Python) with CORS middleware.
*   **Deployment**: Ready for Render deployment with native blueprint configuration (`render.yaml`).
*   **Server**: Gunicorn WSGI server.

---

## 🚀 Local Setup

1.  **Clone the repository**:
    ```bash
    git clone <your-repository-url>
    cd KarshakMitra_web
    ```

2.  **Create and activate a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application**:
    ```bash
    python app.py
    ```
    Open `http://127.0.0.1:5000` in your web browser.

---

## 🌐 Deployment

The repository is configured for one-click deployment on **Render** using the `render.yaml` blueprint:
1.  Push the code to GitHub.
2.  Go to Render and create a new service from the **Blueprint** option.
3.  Select your repository and deploy.
