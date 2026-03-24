import sys
import os
import logging

# Add the root project folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.masking import mask_text
from models import load_baseline_model, load_bert_model
from config import MODEL_TYPE

logger = logging.getLogger(__name__)

# Load models once at startup
baseline_model = None
bert_model = None
tokenizer = None
label_encoder = None

try:
    if MODEL_TYPE == "baseline":
        logger.info(f"Loading baseline model...")
        baseline_model = load_baseline_model()
    elif MODEL_TYPE == "bert":
        logger.info(f"Loading BERT model...")
        bert_model, tokenizer, label_encoder = load_bert_model()
    else:
        raise ValueError(f"Unknown MODEL_TYPE: {MODEL_TYPE}. Must be 'baseline' or 'bert'.")
    logger.info(f"Models loaded successfully with MODEL_TYPE={MODEL_TYPE}")
except Exception as e:
    logger.error(f"Failed to load models: {e}")
    raise

def classify_email(email_text: str):
    """Classify email into predefined categories with PII masking.
    
    Args:
        email_text (str): The email body text to classify
        
    Returns:
        dict: Classification result with masked email and detected entities
        
    Raises:
        ValueError: If email_text is empty or invalid
        RuntimeError: If model inference fails
    """
    if not email_text or not isinstance(email_text, str):
        raise ValueError("email_text must be a non-empty string")
    
    try:
        # Step 1: Mask PII
        masked_text, entities = mask_text(email_text)
        logger.debug(f"Masked email: {masked_text[:100]}...")
        
        # Step 2: Classification
        if MODEL_TYPE == "baseline":
            if baseline_model is None:
                raise RuntimeError("Baseline model not loaded. Please check logs.")
            category = baseline_model.predict([masked_text])[0]
        elif MODEL_TYPE == "bert":
            if bert_model is None or tokenizer is None or label_encoder is None:
                raise RuntimeError("BERT model not loaded. Please check logs.")
            inputs = tokenizer(masked_text, return_tensors="pt", truncation=True, padding=True)
            outputs = bert_model(**inputs)
            pred = outputs.logits.argmax(dim=1).item()
            category = label_encoder.inverse_transform([pred])[0]
        
        logger.info(f"Email classified as: {category}")
        
        # Step 3: Format Response
        return {
            "input_email_body": email_text,
            "list_of_masked_entities": entities,
            "masked_email": masked_text,
            "category_of_the_email": category
        }
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        raise RuntimeError(f"Classification failed: {str(e)}")
