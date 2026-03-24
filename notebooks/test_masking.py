import os
import sys
import re

# ✅ Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Import masking function
from utils.masking import mask_text

# ✅ Mapping classification to standard labels
LABEL_MAP = {
    'email': 'EMAIL',
    'phone_number': 'PHONE',
    'dob': 'DATE',
    'aadhar_num': 'AADHAR',
    'credit_card': 'CREDIT_CARD',
    'cvv_no': 'CVV',
    'expiry_no': 'EXPIRY',
    # Add 'full_name' or others only if included in ground truth
}

# ✅ Ground truth (manually labeled)
true_entities = [
    ('EMAIL', 'johndoe@example.com'),
    ('PHONE', '9876543210'),
    ('DATE', '01/01/1990'),
    ('AADHAR', '1234 5678 9012'),
    ('CREDIT_CARD', '4111 1111 1111 1111'),
    ('CVV', '123'),
    ('EXPIRY', '09/24'),
]

# ✅ Sample email
email = """
Hello, my name is John Doe. My email is johndoe@example.com, phone: 9876543210.
DOB is 01/01/1990. Aadhar: 1234 5678 9012. Card: 4111 1111 1111 1111, CVV: 123, Expiry: 09/24.
"""

# ✅ Run masking function
masked_email, entity_list = mask_text(email)

# ✅ Debug print
print("📩 Masked Email:\n", masked_email)
print("\n🔍 Detected Entities:")
for ent in entity_list:
    print(ent)

# ✅ Text normalization function
def normalize_text(label, text):
    text = text.lower().strip()
    if label in ['AADHAR', 'CREDIT_CARD', 'PHONE']:
        return re.sub(r'\D', '', text)
    elif label in ['DATE', 'EXPIRY']:
        return re.sub(r'[\s\-]', '/', text)
    return text

# ✅ Normalize and extract predicted entities
predicted_entities = []
for ent in entity_list:
    raw_label = ent.get('label') or ent.get('classification') or ''
    text = ent.get('text') or ent.get('entity') or ''
    std_label = LABEL_MAP.get(raw_label.lower())
    if std_label and text:
        predicted_entities.append((std_label, normalize_text(std_label, text)))

# ✅ Normalize ground truth
true_set = set((label, normalize_text(label, text)) for label, text in true_entities)
pred_set = set(predicted_entities)
correct = true_set & pred_set

# ✅ Calculate metrics
precision = len(correct) / len(pred_set) if pred_set else 0
recall = len(correct) / len(true_set) if true_set else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0
masking_accuracy = recall  # ✅ same as recall

# ✅ Print results
print("\n📊 Evaluation Metrics:")
print(f"✅ Precision: {precision:.2f}")
print(f"✅ Recall: {recall:.2f}")
print(f"✅ F1 Score: {f1:.2f}")
print(f"🎯 Masking Accuracy: {masking_accuracy:.2f}")
print(f"\n✅ Correctly Masked: {correct}")
print(f"❌ Missed (False Negatives): {true_set - correct}")
print(f"⚠️ Wrongly Masked (False Positives): {pred_set - correct}")

