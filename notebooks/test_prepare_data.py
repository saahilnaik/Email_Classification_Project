import sys
import os

# Add the root project folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.prepare_data import load_and_prepare_data
from models.baseline_model import train_baseline_model

# Load data and train
df = load_and_prepare_data("data/support_emails.csv")
train_baseline_model(df)  # This should save baseline_classifier.pkl