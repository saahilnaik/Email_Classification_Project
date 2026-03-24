import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.prepare_data import load_and_prepare_data
from models.baseline_model import train_baseline_model

df = load_and_prepare_data("data/support_emails.csv")

# Train Baseline
train_baseline_model(df)