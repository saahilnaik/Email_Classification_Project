import sys
import os

# Add the root project folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Regex patterns for PII types
REGEX_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_number": r"\b\d{10}\b",
    "dob": r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
    "aadhar_num": r"\b\d{4} \d{4} \d{4}\b",
    "credit_debit_no": r"\b(?:\d[ -]*?){13,16}\b",
    "cvv_no": r"\b\d{3}\b",
    "expiry_no": r"\b(0[1-9]|1[0-2])\/\d{2,4}\b",
}


def mask_text(email_text):
    """Mask PII in email text while preserving correct position tracking.
    
    BUG FIX: Collect all entities first, then mask in reverse order (end-to-start)
    to preserve position information. This prevents position shifts as text is replaced.
    """
    masked_text = email_text
    entity_list = []
    
    # Step 1: Collect all regex matches WITHOUT masking yet
    regex_matches = []  # List of (start, end, label, value)
    for label, pattern in REGEX_PATTERNS.items():
        for match in re.finditer(pattern, email_text):
            start, end = match.start(), match.end()
            entity_value = match.group()
            regex_matches.append((start, end, label, entity_value))
    
    # Step 2: Collect spaCy NER matches WITHOUT masking yet
    spacy_matches = []  # List of (start, end, label, value)
    doc = nlp(email_text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            start, end = ent.start_char, ent.end_char
            entity_value = ent.text
            spacy_matches.append((start, end, "full_name", entity_value))
    
    # Step 3: Combine and sort matches by start position (descending) to mask from end to start
    all_matches = regex_matches + spacy_matches
    all_matches.sort(key=lambda x: x[0], reverse=True)  # Sort by start position, descending
    
    # Step 4: Apply masks in reverse order to preserve positions
    for start, end, label, entity_value in all_matches:
        placeholder = f"[{label}]"
        masked_text = masked_text[:start] + placeholder + masked_text[end:]
        entity_list.append({
            "position": [start, start + len(placeholder)],
            "classification": label,
            "entity": entity_value
        })
    
    # Reverse entity list to maintain chronological order
    entity_list.reverse()
    
    return masked_text, entity_list

