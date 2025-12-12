"""Core logic for comparing extracted label data with user input.

This module handles loading product classifications and comparing
form inputs with AI-extracted values from label images.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional


def _load_classifications() -> List[str]:
    """Load TTB product classifications from JSON file.
    
    Returns
    -------
    List[str]
        List of valid product classification names
    """
    json_path = os.path.join(os.path.dirname(__file__), "classifications.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["classifications"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load classifications.json: {e}")
        return []


# Load classifications at module import
CLASSIFICATIONS = _load_classifications()


def normalize_units(value: str) -> str:
    """Normalize volume and unit representations for comparison.
    
    Handles common variations like:
    - "150L" / "150 L" / "150 l" / "150 Liters" → "150l"
    - "750ml" / "750 ML" / "750 milliliters" → "750ml"
    - "12oz" / "12 fl oz" / "12 ounces" → "12floz"
    
    Parameters
    ----------
    value : str
        Volume string with units
        
    Returns
    -------
    str
        Normalized volume string
    """
    # Convert to lowercase and remove extra spaces
    normalized = value.lower().strip()
    
    # Replace various unit spellings with standardized forms
    normalized = re.sub(r'\b(liter|liters|litre|litres)\b', 'l', normalized)
    normalized = re.sub(r'\b(milliliter|milliliters|millilitre|millilitres|ml)\b', 'ml', normalized)
    normalized = re.sub(r'\b(fl\s*oz|fluid\s*ounce|fluid\s*ounces|ounce|ounces|oz)\b', 'floz', normalized)
    
    # Remove all spaces and non-alphanumeric characters except decimal points
    normalized = re.sub(r'[^\w.]', '', normalized)
    
    return normalized


def compare_fields(
    form_data: Dict[str, str], 
    extracted: Dict[str, Optional[str]]
) -> Dict[str, Dict[str, str]]:
    """Compare user form inputs with AI-extracted label values.

    Parameters
    ----------
    form_data : dict
        User-entered data with keys: 'brand', 'class_type', 'abv', 'net_contents'
    extracted : dict
        AI-extracted values with same keys, values may be None

    Returns
    -------
    dict
        Nested dictionary keyed by field name, each containing:
        - 'user_value': the value entered by user
        - 'extracted_value': the value extracted from label
        - 'status': 'match', 'mismatch', or 'not found'
    """
    report: Dict[str, Dict[str, str]] = {}
    
    for key in ["brand", "class_type", "abv", "net_contents"]:
        user_val = form_data.get(key, "").strip() if form_data.get(key) else ""
        extr_val = extracted.get(key)
        status = "not found"
        
        if extr_val:
            if key == "net_contents":
                # Use smart unit normalization for volume comparison
                if user_val and normalize_units(user_val) == normalize_units(extr_val):
                    status = "match"
                else:
                    status = "mismatch"
            else:
                # For other fields: case-insensitive, ignore punctuation
                def normalize(s: str) -> str:
                    return re.sub(r"\W", "", s).lower()
                
                if user_val and normalize(user_val) == normalize(extr_val):
                    status = "match"
                else:
                    status = "mismatch"
        
        report[key] = {
            "user_value": user_val or "",
            "extracted_value": extr_val or "",
            "status": status,
        }
    
    return report
