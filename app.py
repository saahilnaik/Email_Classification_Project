import logging
import logging.handlers
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from utils.pipeline import classify_email
from config import API_HOST, API_PORT, API_RELOAD, LOG_LEVEL, LOG_FORMAT, LOG_FILE
import uvicorn

# Configure logging
os.makedirs(os.path.dirname(LOG_FILE) or "logs", exist_ok=True)
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

# File handler
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=10485760, backupCount=5  # 10MB per file, keep 5 backups
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)

app = FastAPI(
    title="Email Classification API",
    description="Classifies support emails while masking PII",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class EmailRequest(BaseModel):
    """Request body for email classification."""
    email_body: str = Field(..., min_length=1, description="The email body text to classify")

class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str
    error_code: str

@app.post("/classify_email")
def classify(email: EmailRequest):
    """Classify an email and mask PII.
    
    Args:
        email: EmailRequest with email_body field
        
    Returns:
        Classification result with masked email and detected entities
        
    Raises:
        HTTPException: If classification fails
    """
    try:
        logger.info(f"Received email classification request (length: {len(email.email_body)})")
        result = classify_email(email.email_body)
        logger.info(f"Email classified successfully as: {result['category_of_the_email']}")
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during classification")

@app.get("/")
def root():
    """Root endpoint with API information."""
    from config import MODEL_TYPE
    from utils.pipeline import baseline_model, bert_model

    model_status = "unknown"
    if MODEL_TYPE == "baseline":
        model_status = "loaded" if baseline_model is not None else "not loaded"
    elif MODEL_TYPE == "bert":
        model_status = "loaded" if bert_model is not None else "not loaded"

    return {
        "message": "Email Classification API is running!",
        "version": "1.0.0",
        "model": {
            "type": MODEL_TYPE,
            "status": model_status
        },
        "endpoints": {
            "GET /": "This information page",
            "GET /health": "Health check",
            "POST /classify_email": "Classify email and mask PII",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation",
            "GET /openapi.json": "OpenAPI schema"
        },
        "usage": {
            "local_access": f"http://localhost:{API_PORT}",
            "network_access": f"http://YOUR_IP:{API_PORT}",
            "docs": f"http://localhost:{API_PORT}/docs",
            "test_email": f"POST to http://localhost:{API_PORT}/classify_email"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("="*60)
    logger.info(f"SERVER BINDING: {API_HOST}:{API_PORT} (listening on all interfaces)")
    logger.info("="*60)

    # Test model loading before starting server
    try:
        from utils.pipeline import baseline_model, bert_model
        from config import MODEL_TYPE
        if MODEL_TYPE == "baseline" and baseline_model is None:
            logger.error("Baseline model failed to load. Please check model files.")
            exit(1)
        elif MODEL_TYPE == "bert" and (bert_model is None):
            logger.error("BERT model failed to load. Please check model files.")
            exit(1)
        logger.info(f"Model loaded successfully: {MODEL_TYPE}")
    except Exception as e:
        logger.error(f"Model loading error: {e}")
        exit(1)

    logger.info("ACCESS URLs:")
    logger.info(f"  Local:     http://localhost:{API_PORT}")
    logger.info(f"  Local:     http://127.0.0.1:{API_PORT}")

    # Get local IP for network access instructions
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"  Network:   http://{local_ip}:{API_PORT}")
    except Exception:
        logger.info(f"  Network:   http://YOUR_IP:{API_PORT}")

    logger.info("="*60)
    logger.info("API Documentation:")
    logger.info(f"  Swagger UI: http://localhost:{API_PORT}/docs")
    logger.info(f"  ReDoc:      http://localhost:{API_PORT}/redoc")
    logger.info("="*60)

    if API_HOST == "0.0.0.0":
        logger.info("Note: Server binds to 0.0.0.0 (all interfaces) for network access")
        logger.info("But you access it via localhost or your IP address, NOT 0.0.0.0")

    uvicorn.run("app:app", host=API_HOST, port=API_PORT, reload=API_RELOAD)
