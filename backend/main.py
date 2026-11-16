import io
import time
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image

from .yolo_service import yolo_engine
from .resume_service import resume_engine

app = FastAPI(
    title="Unified Vision & ATS Resume AI Server",
    description="Full-stack API serving YOLOv11 Computer Vision and Multi-Model ATS Resume Intelligence",
    version="2.0.0"
)

# Enable CORS for local and web frontend dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextAnalysisRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None


@app.get("/")
def read_root():
    return {
        "title": "Unified Vision & ATS Resume AI API",
        "status": "online",
        "docs_url": "/docs",
        "vision_model": yolo_engine.model_path,
        "resume_models_connected": list(resume_engine.models.keys()),
        "semantic_encoder_loaded": resume_engine.encoder_loaded
    }

@app.get("/health")
def health_check():
    return {
        "status": "ready",
        "vision_engine": {
            "model": yolo_engine.model_path,
            "is_loaded": yolo_engine.is_loaded
        },
        "resume_engine": {
            "connected_models": list(resume_engine.models.keys()),
            "encoder_ready": resume_engine.encoder_loaded,
            "device": str(resume_engine.device)
        }
    }

# -------------------------------------------------------------
# YOLOv11 Computer Vision Endpoints
# -------------------------------------------------------------
@app.post("/predict/image")
async def predict_image(
    file: UploadFile = File(...),
    confidence: float = Form(0.40),
    iou: float = Form(0.45)
):
    """Runs YOLOv11 object detection on an uploaded image."""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        result = yolo_engine.predict(image=image, confidence=confidence, iou=iou)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision inference error: {str(e)}")

@app.post("/model/load")
def switch_model(model_path: str = Form(...)):
    """Dynamically switch YOLOv11 model weights file."""
    try:
        yolo_engine.load_model(model_path)
        return {
            "status": "success",
            "active_model": model_path,
            "is_loaded": yolo_engine.is_loaded
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load vision model: {str(e)}")

@app.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live webcam object detection."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            image = Image.open(io.BytesIO(data)).convert("RGB")
            result = yolo_engine.predict(image=image, confidence=0.35, iou=0.45)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close()

# -------------------------------------------------------------
# ATS Resume & Connected AI Models Endpoints (Zety-Style)
# -------------------------------------------------------------
@app.get("/api/resume/models")
def get_resume_models():
    """Returns details and classes for all connected resume classification models."""
    info = {}
    for k, v in resume_engine.models.items():
        info[k] = {
            "num_classes": v["num_classes"],
            "classes": v["classes"],
            "weights": v["weights"]
        }
    return {
        "status": "success",
        "semantic_encoder": "anass1209/resume-job-matcher-all-MiniLM-L6-v2",
        "connected_models": info
    }

@app.post("/api/resume/analyze-text")
def analyze_resume_text(req: TextAnalysisRequest):
    """
    Evaluates raw resume text against ATS rules and runs classification
    across all connected models (Archive 123, Archive 456, and Archive 2).
    Optionally evaluates semantic fit against a job description.
    """
    try:
        analysis = resume_engine.analyze_ats_resume(
            text=req.resume_text,
            job_description=req.job_description
        )
        return JSONResponse(content=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/api/resume/analyze-pdf")
async def analyze_resume_pdf(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    """
    Upload a resume PDF directly: parses text, generates ATS score,
    checks readability, metrics, sections, and runs all connected models.
    """
    try:
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        text = resume_engine.extract_text_from_pdf(pdf_file)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract readable text from PDF")

        analysis = resume_engine.analyze_ats_resume(
            text=text,
            job_description=job_description
        )
        analysis["file_name"] = file.filename
        return JSONResponse(content=analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
