import os
from logging import INFO, DEBUG

# Model Configuration
MODEL_TYPE = os.getenv("MODEL_TYPE", "baseline")  # or "bert"

# Data Paths
DATA_PATH = os.getenv("DATA_PATH", "data/support_emails.csv")
BASELINE_MODEL_PATH = os.getenv("BASELINE_MODEL_PATH", "models/baseline_classifier.pkl")
BERT_MODEL_PATH = os.getenv("BERT_MODEL_PATH", "models/bert_classifier")
BERT_LABEL_ENCODER_PATH = os.getenv("BERT_LABEL_ENCODER_PATH", "models/bert_label_encoder.pkl")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# Logging Configuration
LOG_LEVEL = int(os.getenv("LOG_LEVEL", str(INFO)))
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
