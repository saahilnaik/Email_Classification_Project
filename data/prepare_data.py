import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from utils.masking import mask_text


def load_and_prepare_data(filepath):
    df = pd.read_csv(filepath)  # or .json, based on your format

    masked_texts = []
    for text in df["email_text"]:
        masked, _ = mask_text(text)
        masked_texts.append(masked)

    df["masked_text"] = masked_texts
    return df[["masked_text", "category"]]
