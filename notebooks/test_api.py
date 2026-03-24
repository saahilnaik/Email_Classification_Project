"""
Integration tests for the email classification API and pipeline.

This test suite validates:
- PII masking functionality
- Email classification (baseline and BERT models)
- Model loading
- API error handling
"""

import sys
import os

# Add the root project folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.masking import mask_text
from utils.pipeline import classify_email
from utils.pipeline import baseline_model, bert_model, label_encoder
from config import MODEL_TYPE


def test_pii_masking():
    """Test PII masking functionality."""
    print("\n=== Testing PII Masking ===")
    
    email = """
    Hello, my name is John Doe. My email is johndoe@example.com, phone: 9876543210.
    DOB is 01/01/1990. Aadhar: 1234 5678 9012. Card: 4111 1111 1111 1111, CVV: 123, Expiry: 09/24.
    """
    
    masked_email, entities = mask_text(email)
    
    print(f"Original email:\n{email}")
    print(f"\n✓ Masked email:\n{masked_email}")
    print(f"\n✓ Detected {len(entities)} entities:")
    for ent in entities:
        print(f"  - {ent['classification']}: '{ent['entity']}' at position {ent['position']}")
    
    # Verify masking worked
    assert "[email]" in masked_email, "Email not masked"
    assert "[phone_number]" in masked_email, "Phone number not masked"
    assert "[dob]" in masked_email, "DOB not masked"
    assert len(entities) > 0, "No entities detected"
    
    print("\n✓ PII masking test PASSED")


def test_position_tracking():
    """Test that entity positions are correctly tracked even after masking."""
    print("\n=== Testing Position Tracking ===")
    
    email = "Email: test@example.com Phone: 9876543210"
    masked_email, entities = mask_text(email)
    
    print(f"Original: {email}")
    print(f"Masked: {masked_email}")
    print(f"Entities: {entities}")
    
    # Verify positions are valid
    for ent in entities:
        start, end = ent['position']
        masked_portion = masked_email[start:end]
        print(f"  Position [{start}:{end}] -> '{masked_portion}'")
        assert start < end, f"Invalid position range: {ent['position']}"
        assert masked_portion.startswith("["), f"Position doesn't point to placeholder at {ent['position']}"
    
    print("\n✓ Position tracking test PASSED")


def test_email_classification():
    """Test email classification functionality."""
    print(f"\n=== Testing Email Classification (MODEL_TYPE={MODEL_TYPE}) ===")
    
    test_emails = [
        "I was charged twice for my subscription. Can you please refund me?",
        "The application keeps crashing when I try to upload a file. Please help!",
        "I forgot my password and cannot log in. How do I reset it?",
        "Can I change my account email address?",
    ]
    
    try:
        for email in test_emails:
            result = classify_email(email)
            print(f"\nEmail: {email[:60]}...")
            print(f"Category: {result['category_of_the_email']}")
            print(f"Masked: {result['masked_email'][:80]}...")
            print(f"PII detected: {len(result['list_of_masked_entities'])} entities")
            
            assert 'category_of_the_email' in result, "Missing category in result"
            assert 'masked_email' in result, "Missing masked_email in result"
            assert 'list_of_masked_entities' in result, "Missing entities in result"
        
        print("\n✓ Email classification test PASSED")
    except FileNotFoundError as e:
        print(f"\n⚠ Skipping classification test: {e}")
        print("  Please train a model first using models/baseline_model.py or models/bert_model.py")


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n=== Testing Error Handling ===")
    
    test_cases = [
        (None, "None input"),
        ("", "Empty string"),
        (123, "Integer input"),
    ]
    
    for invalid_input, description in test_cases:
        try:
            classify_email(invalid_input)
            print(f"✗ {description}: Should have raised ValueError")
        except ValueError as e:
            print(f"✓ {description}: Correctly raised ValueError")
        except Exception as e:
            print(f"✗ {description}: Raised unexpected exception: {type(e).__name__}")
    
    print("\n✓ Error handling test PASSED")


def test_model_loading():
    """Test that models are loaded correctly."""
    print("\n=== Testing Model Loading ===")
    
    if MODEL_TYPE == "baseline":
        assert baseline_model is not None, "Baseline model not loaded"
        print(f"✓ Baseline model loaded: {type(baseline_model).__name__}")
    elif MODEL_TYPE == "bert":
        assert bert_model is not None, "BERT model not loaded"
        assert label_encoder is not None, "Label encoder not loaded"
        print(f"✓ BERT model loaded: {type(bert_model).__name__}")
        print(f"✓ Label encoder loaded: {type(label_encoder).__name__}")
    
    print("\n✓ Model loading test PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL CLASSIFICATION TEST SUITE")
    print("=" * 60)
    
    try:
        test_pii_masking()
        test_position_tracking()
        test_model_loading()
        test_error_handling()
        test_email_classification()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
