# Email Classification System with PII Masking

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview

This project implements an intelligent email classification system that automatically categorizes support emails while protecting sensitive information through PII (Personally Identifiable Information) masking. The system uses machine learning models to classify emails into predefined categories and employs both regex-based patterns and NLP techniques to identify and mask sensitive data.

## Tech Stack

- **Language**: Python 3.8+
- **Web Framework**: FastAPI
- **ML Frameworks**:
  - Hugging Face Transformers (DistilBERT)
  - PyTorch
  - scikit-learn (SVM baseline)
  - spaCy (Named Entity Recognition)
- **Data Processing**: pandas, NumPy
- **Deployment**: Uvicorn ASGI server

## Project Structure

```
Email Classification Project/
├── app.py                          # FastAPI web service (entry point)
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── LICENSE                         # GNU GPLv3 license
├── .gitignore                      # Git ignore rules
│
├── models/                         # ML model definitions and saved models
│   ├── __init__.py                # Model loading utilities
│   ├── baseline_model.py          # SVM + TF-IDF classifier
│   ├── bert_model.py              # DistilBERT classifier
│   └── bert_classifier/           # Pre-trained BERT weights & tokenizer
│
├── utils/                          # Core utility modules
│   ├── masking.py                 # PII detection and masking
│   └── pipeline.py                # Main classification pipeline
│
├── data/                           # Data processing and datasets
│   ├── prepare_data.py            # Data loading and preprocessing
│   └── support_emails.csv         # Training dataset
│
└── notebooks/                      # Testing and validation scripts
    ├── test_masking.py            # PII masking validation
    ├── test_baseline_model.py     # SVM model testing
    ├── test_bert_model.py         # BERT model testing
    ├── test_prepare_data.py       # Data processing validation
    └── compute_metrics.py         # Performance metrics calculation
```

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd email-classification-project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## 🚨 CRITICAL: Correct URLs to Use

**❌ NEVER use this (INVALID):** `http://0.0.0.0:8000`
**✅ Use these instead:**

### Local Access (same device):
- `http://localhost:8000`
- `http://127.0.0.1:8000`

### Network Access (other devices):
- `http://192.168.1.9:8000` (your current IP address)

**Why 0.0.0.0 doesn't work:** `0.0.0.0` is the server's listening address (bind to all interfaces), not a browseable URL.

### API Endpoint

**POST** `/classify_email`

**Request Body**:
```json
{
  "email_body": "Hello, my name is John Doe. My email is johndoe@example.com, phone: 9876543210. DOB is 01/01/1990."
}
```

**Response**:
```json
{
  "input_email_body": "Hello, my name is John Doe. My email is johndoe@example.com, phone: 9876543210. DOB is 01/01/1990.",
  "list_of_masked_entities": [
    {
      "position": [25, 36],
      "classification": "full_name",
      "entity": "John Doe"
    },
    {
      "position": [47, 66],
      "classification": "email",
      "entity": "johndoe@example.com"
    },
    {
      "position": [75, 85],
      "classification": "phone_number",
      "entity": "9876543210"
    },
    {
      "position": [95, 105],
      "classification": "dob",
      "entity": "01/01/1990"
    }
  ],
  "masked_email": "Hello, my name is [full_name]. My email is [email], phone: [phone_number]. DOB is [dob].",
  "category_of_the_email": "Account"
}
```

### Model Configuration

Edit `config.py` to switch between models:
```python
MODEL_TYPE = "baseline"  # Use SVM + TF-IDF
# MODEL_TYPE = "bert"    # Use DistilBERT
```

## Environment Variables

The application uses the following configuration variables (defined in `config.py`):

- `MODEL_TYPE`: Choose between "baseline" (SVM) or "bert" (DistilBERT)
- `DATA_PATH`: Path to the training dataset CSV file

## Scripts

### Training Scripts

**Train Baseline Model**:
```bash
python -c "from models.baseline_model import train_baseline_model; from data.prepare_data import load_and_prepare_data; df = load_and_prepare_data('data/support_emails.csv'); train_baseline_model(df)"
```

**Train BERT Model**:
```bash
python -c "from models.bert_model import train_bert_model; from data.prepare_data import load_and_prepare_data; df = load_and_prepare_data('data/support_emails.csv'); train_bert_model(df)"
```

### Testing Scripts

Run individual test scripts from the `notebooks/` directory:
```bash
python notebooks/test_masking.py
python notebooks/test_baseline_model.py
python notebooks/test_bert_model.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Features

- **PII Masking**: Automatically detects and masks sensitive information including:
  - Email addresses
  - Phone numbers
  - Dates of birth
  - Aadhar numbers
  - Credit/debit card numbers
  - CVV numbers
  - Expiry dates
  - Full names (via spaCy NER)

- **Email Classification**: Supports multiple ML models:
  - Baseline: SVM with TF-IDF vectorization
  - Advanced: Fine-tuned DistilBERT transformer

- **REST API**: FastAPI-based web service for easy integration
- **Extensible**: Easy to add new PII patterns or classification categories
- **Production Ready**: Includes proper error handling and logging

## Performance

- **Baseline Model**: Fast inference, suitable for resource-constrained environments
- **BERT Model**: Higher accuracy, requires more computational resources
- **PII Masking**: Sub-millisecond processing for typical email lengths

### Firewall Configuration

If you're having trouble accessing from other devices, you may need to:

**Windows Firewall:**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → TCP → Specific port: 8000
5. Allow the connection
6. Name it "Email Classification API"

**Or temporarily disable firewall for testing:**
```cmd
netsh advfirewall set allprofiles state off
```

**Re-enable firewall after testing:**
```cmd
netsh advfirewall set allprofiles state on
```

### Logs

Check the console output for detailed error messages and performance metrics.