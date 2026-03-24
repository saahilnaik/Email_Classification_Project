import logging
import logging.handlers
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
    """Root endpoint - serves the interactive dashboard for email classification testing."""
    html_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file, media_type="text/html")
    else:
        # Fallback if HTML file not found
        return {
            "error": "Dashboard not found",
            "message": "HTML dashboard file is missing",
            "fallback_endpoints": {
                "GET /docs": "Swagger UI API Documentation",
                "GET /redoc": "ReDoc API Documentation",
                "GET /api/info": "API Information and Metadata"
            }
        }

@app.get("/api/info")
def api_info():
    """API information and metadata endpoint."""
    from config import MODEL_TYPE
    from utils.pipeline import baseline_model, bert_model

    model_status = "unknown"
    if MODEL_TYPE == "baseline":
        model_status = "loaded" if baseline_model is not None else "not loaded"
    elif MODEL_TYPE == "bert":
        model_status = "loaded" if bert_model is not None else "not loaded"

    return {
        "name": "Email Classification API",
        "version": "1.0.0",
        "description": "Classifies support emails while masking PII",
        "model": {
            "type": MODEL_TYPE,
            "status": model_status
        },
        "endpoints": {
            "GET /": "Interactive dashboard for testing emails (THE MAIN PAGE)",
            "GET /docs": "Swagger UI - Interactive API documentation",
            "GET /redoc": "ReDoc - Beautiful alternative API documentation",
            "GET /health": "Health check endpoint",
            "GET /api/info": "API information and metadata (this page)",
            "GET /openapi.json": "OpenAPI schema in JSON format",
            "POST /classify_email": "Classify email and mask PII"
        },
        "access_urls": {
            "dashboard": f"http://localhost:{API_PORT}",
            "swagger_docs": f"http://localhost:{API_PORT}/docs",
            "redoc_docs": f"http://localhost:{API_PORT}/redoc",
            "network_access": f"http://YOUR_DEVICE_IP:{API_PORT}"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("="*70)
    logger.info("Email Classification API - Starting Server")
    logger.info("="*70)
    logger.info(f"Server Binding: {API_HOST}:{API_PORT} (listening on all interfaces)")

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
        logger.info(f"Model Loaded: {MODEL_TYPE}")
    except Exception as e:
        logger.error(f"Model loading error: {e}")
        exit(1)

    logger.info("="*70)
    logger.info("IMPORTANT: Access the following URLs in your browser:")
    logger.info("="*70)
    
    logger.info("")
    logger.info("1. MAIN DASHBOARD (Test your emails here):")
    logger.info(f"   --> http://localhost:{API_PORT}")
    logger.info(f"   --> http://127.0.0.1:{API_PORT}")
    logger.info("   This is your testing interface with a beautiful UI.")
    
    # Get local IP for network access instructions
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"   --> http://{local_ip}:{API_PORT} (Network access)")
    except Exception:
        logger.info(f"   --> http://YOUR_IP:{API_PORT} (Network access)")

    logger.info("")
    logger.info("2. SWAGGER UI DOCUMENTATION (Interactive API docs):")
    logger.info(f"   --> http://localhost:{API_PORT}/docs")
    logger.info("   Test API endpoints directly and read parameter details.")
    
    logger.info("")
    logger.info("3. REDOC DOCUMENTATION (Alternative beautiful docs):")
    logger.info(f"   --> http://localhost:{API_PORT}/redoc")
    logger.info("   Alternative documentation format for the API.")

    logger.info("")
    logger.info("4. HEALTH CHECK:")
    logger.info(f"   --> http://localhost:{API_PORT}/health")
    logger.info("   Verify the server is running.")

    logger.info("")
    logger.info("5. API METADATA:")
    logger.info(f"   --> http://localhost:{API_PORT}/api/info")
    logger.info("   View all available endpoints and their descriptions.")

    logger.info("="*70)
    
    if API_HOST == "0.0.0.0":
        logger.info("Note: Server binds to 0.0.0.0 to accept connections from all")
        logger.info("      network interfaces. Access via localhost or your IP, NOT 0.0.0.0")
    
    logger.info("="*70)

    uvicorn.run("app:app", host=API_HOST, port=API_PORT, reload=API_RELOAD)
