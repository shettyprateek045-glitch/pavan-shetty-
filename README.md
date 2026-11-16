# Unified AI Intelligence Hub: YOLOv11 Vision & ATS Resume Checker

Production-ready framework combining **Ultralytics YOLOv11** computer vision inference with a **Multi-Model ATS Resume Intelligence Platform** modeled after top enterprise ATS checkers (Zety).

---

## 🌟 Key Features

### 1. 👁️ YOLOv11 Computer Vision Suite
- **Interactive Vision Dashboard (`index.html`)**: Real-time object detection via Image upload, live webcam streaming, and simulated preview.
- **FastAPI Backend Server (`backend/main.py`)**: High-throughput REST API and WebSocket streaming endpoint (`/ws/stream`).
- **Complete Pipeline**: Training (`train.py`), Validation (`val.py`), Inference (`predict.py`), and Model Export (`export.py`).

### 2. 📄 Zety-Style ATS Resume Checker & Multi-Model Intelligence
- **Overall ATS Readability Score (0-100)**: Real-time gauge and audit assessing ATS pass probability.
- **Mandatory Sections Audit**: Automatically detects Contact Info, Professional Summary, Work Experience, Education, Skills, Projects, and Certifications.
- **Measurable Metrics & Action Verbs**: Scans for quantifiable impact numbers and strong action verbs.
- **Semantic Job Description Matcher**: Cosine similarity against target job postings with matched & missing keyword analysis.
- **Multi-Model Connected AI Hub**:
  - **Archive 123 Model**: 24 Broad Industry Categories (PDF and text-based)
  - **Archive 456 Model**: 25 Specialized Technical & Engineering Domains (**99.48%** validation accuracy)
  - **Archive 2 Model**: 9 Enterprise IT & Architecture Domains (**84.60%** validation accuracy)
  - **Pretrained Semantic Transformer**: `anass1209/resume-job-matcher-all-MiniLM-L6-v2` (384-dimensional dense semantic vectors)

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 2. Start the Unified Server (Local or Cloud Deployment)
```bash
# Run root server entrypoint (auto-detects $PORT and serves dashboard at /)
python app.py

# Or run with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000
```

Interactive API documentation available at: `http://localhost:8000/docs`
Web Dashboard served directly at: `http://localhost:8000/`

### 3. Cloud Deployment (Onslate / Render / Railway / Heroku)
The repository includes production configuration for cloud PaaS hosting platforms:
- **`app.py`**: Binds to `0.0.0.0` and reads dynamic `$PORT` environment variable.
- **`Procfile`**: `web: uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}`
- **`start.sh`**: Shell entrypoint for container runtimes.
- **`package.json`**: NPM start scripts for hybrid and Node/Python buildpacks.
- **`index.html`**: Automatically connects to the current host origin (`window.location.origin`) to prevent connection refused errors in cloud environments.

---

## 📊 API Endpoints

- `GET /health` — Health check status for vision & resume engines.
- `POST /predict/image` — YOLOv11 image detection with bounding boxes & latency.
- `POST /api/resume/analyze-pdf` — Full ATS report & multi-model classification from an uploaded PDF.
- `POST /api/resume/analyze-text` — ATS audit and job description semantic match from raw text.
- `GET /api/resume/models` — Registry of all connected PyTorch and Transformer models.
