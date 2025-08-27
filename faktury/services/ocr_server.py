#!/usr/bin/env python3
"""
OCR Processing Server
Provides HTTP API for OCR processing using open-source engines
"""

import os
import sys
import asyncio
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

# Add the project root to Python path
sys.path.insert(0, '/app')

try:
    from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    import uvicorn
    from pydantic import BaseModel
except ImportError as e:
    print(f"FastAPI dependencies not installed: {e}")
    print("Please install: pip install fastapi uvicorn")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OCR_SERVICE_PORT = int(os.getenv('OCR_SERVICE_PORT', 8001))
OCR_WORKERS = int(os.getenv('OCR_WORKERS', 2))
OCR_MAX_CONCURRENT_JOBS = int(os.getenv('OCR_MAX_CONCURRENT_JOBS', 4))
TESSERACT_TIMEOUT = int(os.getenv('TESSERACT_TIMEOUT', 30))
EASYOCR_GPU = os.getenv('EASYOCR_GPU', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Directories
OCR_TEMP_DIR = Path(os.getenv('OCR_TEMP_DIR', '/app/temp'))
OCR_MODELS_DIR = Path(os.getenv('OCR_MODELS_DIR', '/app/models'))
OCR_UPLOAD_DIR = Path(os.getenv('OCR_UPLOAD_DIR', '/app/uploads'))

# Create directories
OCR_TEMP_DIR.mkdir(parents=True, exist_ok=True)
OCR_MODELS_DIR.mkdir(parents=True, exist_ok=True)
OCR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# FastAPI app
app = FastAPI(
    title="FaktuLove OCR Service",
    description="Open-source OCR processing service for Polish invoices",
    version="1.0.0"
)

# Global OCR engines (will be initialized on startup)
ocr_engines = {}
processing_jobs = {}

class OCRRequest(BaseModel):
    """OCR processing request model"""
    engine: str = "auto"  # tesseract, easyocr, or auto
    language: str = "pol+eng"
    preprocessing: bool = True
    confidence_threshold: float = 0.5

class OCRResponse(BaseModel):
    """OCR processing response model"""
    job_id: str
    status: str
    text: Optional[str] = None
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    engine_used: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    engines: Dict[str, bool]
    version: str
    uptime: float

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize OCR engines on startup"""
    logger.info("Starting OCR service...")
    
    # Initialize OCR engines
    await initialize_ocr_engines()
    
    logger.info(f"OCR service started on port {OCR_SERVICE_PORT}")

async def initialize_ocr_engines():
    """Initialize OCR engines"""
    global ocr_engines
    
    logger.info("Initializing OCR engines...")
    
    # Initialize Tesseract
    try:
        import pytesseract
        # Test Tesseract
        version = pytesseract.get_tesseract_version()
        langs = pytesseract.get_languages()
        
        if 'pol' in langs:
            ocr_engines['tesseract'] = {
                'available': True,
                'version': str(version),
                'languages': langs
            }
            logger.info(f"Tesseract initialized: {version}")
        else:
            logger.warning("Tesseract available but Polish language not found")
            ocr_engines['tesseract'] = {'available': False, 'error': 'Polish language not available'}
            
    except Exception as e:
        logger.error(f"Failed to initialize Tesseract: {e}")
        ocr_engines['tesseract'] = {'available': False, 'error': str(e)}
    
    # Initialize EasyOCR
    try:
        import easyocr
        reader = easyocr.Reader(['pl', 'en'], gpu=EASYOCR_GPU)
        ocr_engines['easyocr'] = {
            'available': True,
            'reader': reader,
            'gpu': EASYOCR_GPU
        }
        logger.info(f"EasyOCR initialized (GPU: {EASYOCR_GPU})")
        
    except Exception as e:
        logger.error(f"Failed to initialize EasyOCR: {e}")
        ocr_engines['easyocr'] = {'available': False, 'error': str(e)}
    
    # Initialize OpenCV
    try:
        import cv2
        ocr_engines['opencv'] = {
            'available': True,
            'version': cv2.__version__
        }
        logger.info(f"OpenCV initialized: {cv2.__version__}")
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenCV: {e}")
        ocr_engines['opencv'] = {'available': False, 'error': str(e)}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    import time
    
    engines_status = {}
    for engine, config in ocr_engines.items():
        engines_status[engine] = config.get('available', False)
    
    return HealthResponse(
        status="healthy" if any(engines_status.values()) else "unhealthy",
        engines=engines_status,
        version="1.0.0",
        uptime=time.time()  # Simplified uptime
    )

@app.post("/process", response_model=OCRResponse)
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    engine: str = "auto",
    language: str = "pol+eng",
    preprocessing: bool = True,
    confidence_threshold: float = 0.5
):
    """Process document with OCR"""
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Validate file type
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    # Validate file size (10MB limit)
    max_size = 10 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {len(file_content)} bytes (max: {max_size})"
        )
    
    # Initialize job status
    processing_jobs[job_id] = {
        'status': 'queued',
        'created_at': asyncio.get_event_loop().time()
    }
    
    # Start background processing
    background_tasks.add_task(
        process_document_background,
        job_id,
        file_content,
        file.content_type,
        engine,
        language,
        preprocessing,
        confidence_threshold
    )
    
    return OCRResponse(
        job_id=job_id,
        status="queued"
    )

@app.get("/status/{job_id}", response_model=OCRResponse)
async def get_job_status(job_id: str):
    """Get processing job status"""
    
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    
    return OCRResponse(
        job_id=job_id,
        status=job['status'],
        text=job.get('text'),
        confidence=job.get('confidence'),
        processing_time=job.get('processing_time'),
        engine_used=job.get('engine_used'),
        error=job.get('error')
    )

async def process_document_background(
    job_id: str,
    file_content: bytes,
    content_type: str,
    engine: str,
    language: str,
    preprocessing: bool,
    confidence_threshold: float
):
    """Background task for document processing"""
    
    import time
    start_time = time.time()
    
    try:
        # Update job status
        processing_jobs[job_id]['status'] = 'processing'
        
        # Save file temporarily
        temp_file = OCR_TEMP_DIR / f"{job_id}_{int(time.time())}"
        temp_file.write_bytes(file_content)
        
        try:
            # Process with selected engine
            if engine == "auto":
                result = await process_with_best_engine(temp_file, language, preprocessing)
            elif engine == "tesseract":
                result = await process_with_tesseract(temp_file, language, preprocessing)
            elif engine == "easyocr":
                result = await process_with_easyocr(temp_file, language, preprocessing)
            else:
                raise ValueError(f"Unknown engine: {engine}")
            
            # Update job with results
            processing_time = time.time() - start_time
            processing_jobs[job_id].update({
                'status': 'completed',
                'text': result['text'],
                'confidence': result['confidence'],
                'processing_time': processing_time,
                'engine_used': result['engine']
            })
            
        finally:
            # Clean up temporary file
            if temp_file.exists():
                temp_file.unlink()
                
    except Exception as e:
        logger.error(f"Processing failed for job {job_id}: {e}")
        processing_jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'processing_time': time.time() - start_time
        })

async def process_with_best_engine(temp_file: Path, language: str, preprocessing: bool) -> Dict[str, Any]:
    """Process with the best available engine"""
    
    # Try EasyOCR first (usually more accurate)
    if ocr_engines.get('easyocr', {}).get('available'):
        try:
            return await process_with_easyocr(temp_file, language, preprocessing)
        except Exception as e:
            logger.warning(f"EasyOCR failed, trying Tesseract: {e}")
    
    # Fallback to Tesseract
    if ocr_engines.get('tesseract', {}).get('available'):
        return await process_with_tesseract(temp_file, language, preprocessing)
    
    raise RuntimeError("No OCR engines available")

async def process_with_tesseract(temp_file: Path, language: str, preprocessing: bool) -> Dict[str, Any]:
    """Process with Tesseract OCR"""
    
    if not ocr_engines.get('tesseract', {}).get('available'):
        raise RuntimeError("Tesseract not available")
    
    import pytesseract
    from PIL import Image
    
    # Load image
    if preprocessing:
        image = await preprocess_image(temp_file)
    else:
        image = Image.open(temp_file)
    
    # Extract text with confidence
    data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
    
    # Calculate confidence
    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Extract text
    text = pytesseract.image_to_string(image, lang=language)
    
    return {
        'text': text.strip(),
        'confidence': avg_confidence / 100.0,  # Convert to 0-1 scale
        'engine': 'tesseract'
    }

async def process_with_easyocr(temp_file: Path, language: str, preprocessing: bool) -> Dict[str, Any]:
    """Process with EasyOCR"""
    
    if not ocr_engines.get('easyocr', {}).get('available'):
        raise RuntimeError("EasyOCR not available")
    
    import numpy as np
    from PIL import Image
    
    reader = ocr_engines['easyocr']['reader']
    
    # Load and preprocess image
    if preprocessing:
        image = await preprocess_image(temp_file)
    else:
        image = Image.open(temp_file)
    
    # Convert to numpy array
    image_array = np.array(image)
    
    # Extract text
    results = reader.readtext(image_array)
    
    # Combine results
    text_parts = []
    confidences = []
    
    for (bbox, text, confidence) in results:
        text_parts.append(text)
        confidences.append(confidence)
    
    # Calculate average confidence
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Combine text
    full_text = '\n'.join(text_parts)
    
    return {
        'text': full_text.strip(),
        'confidence': avg_confidence,
        'engine': 'easyocr'
    }

async def preprocess_image(temp_file: Path) -> Image.Image:
    """Preprocess image for better OCR results"""
    
    import cv2
    import numpy as np
    from PIL import Image
    
    # Load image
    if temp_file.suffix.lower() == '.pdf':
        # Convert PDF to image
        from pdf2image import convert_from_path
        images = convert_from_path(temp_file, first_page=1, last_page=1)
        image = images[0]
        image_array = np.array(image)
    else:
        image = Image.open(temp_file)
        image_array = np.array(image)
    
    # Convert to grayscale
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_array
    
    # Apply preprocessing
    # 1. Noise reduction
    denoised = cv2.medianBlur(gray, 3)
    
    # 2. Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # 3. Thresholding
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Convert back to PIL Image
    return Image.fromarray(binary)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "ocr_server:app",
        host="0.0.0.0",
        port=OCR_SERVICE_PORT,
        workers=OCR_WORKERS,
        log_level=LOG_LEVEL.lower()
    )