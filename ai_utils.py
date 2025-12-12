"""OpenAI GPT-4 Vision integration for AI-powered label field extraction.

This module handles communication with OpenAI's API to extract brand name,
product classification, ABV, and net contents from alcohol label images.
"""

import os
import json
import base64
from typing import Dict, Optional, List, Tuple

from label_processor import CLASSIFICATIONS


def _b64_data_url(image_bytes: bytes, mime_type: str) -> str:
    """Convert image bytes to base64 data URL for API transmission.
    
    Parameters
    ----------
    image_bytes : bytes
        Raw image data
    mime_type : str
        MIME type (e.g., 'image/png', 'image/jpeg')
        
    Returns
    -------
    str
        Base64-encoded data URL
    """
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def ai_extract_fields(
    text: str,
    images: Optional[List[Tuple[bytes, str]]] = None,
) -> Optional[Dict[str, str]]:
    """Extract label fields using OpenAI's GPT-4 Vision model.
    
    Sends OCR text and label images to OpenAI's API to extract:
    - Brand name
    - Product class/type (from 300+ TTB classifications)
    - Alcohol by Volume (ABV)
    - Net contents
    
    Parameters
    ----------
    text : str
        Combined OCR text from all label images
    images : Optional[List[Tuple[bytes, str]]]
        List of (image_bytes, mime_type) tuples for vision analysis
        
    Returns
    -------
    Optional[Dict[str, str]]
        Dictionary with keys: brand, class_type, abv, net_contents
        Returns None if API key missing or all fields are None
    """
    print("AI extraction running...")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No OPENAI_API_KEY found")
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        classes_str = "\n".join(f"- {c}" for c in CLASSIFICATIONS)

        system_msg = (
            "You are an expert in alcohol beverage labeling.\n"
            "Extract the following fields from the label:\n"
            "  - brand: the main commercial brand name on the label.\n"
            "    Do NOT return importer text, UPC text, websites, warnings, slogans, or varietals (Merlot, IPA, Rose).\n"
            "  - class_type: the product class/type from the allowed list provided.\n"
            "    IMPORTANT: Match the EXACT spelling from the list, including 'WHISKY' vs 'WHISKEY' distinctions.\n"
            "  - abv: the alcohol by volume percentage (e.g., '40%', '12.5%'). Include the % symbol.\n"
            "  - net_contents: the volume with units (e.g., '750 ml', '1 liter', '12 fl oz').\n"
            "If you cannot determine a field, use null.\n"
            "Respond ONLY with a compact JSON object."
        )

        user_instructions = (
            "Use both the OCR text and the images (if provided). OCR can be wrong for stylized fonts.\n\n"
            f"OCR text:\n{text}\n\n"
            f"Allowed product classes:\n{classes_str}\n\n"
            "CRITICAL: For class_type, you MUST use the EXACT spelling from the list above.\n"
            "Pay special attention to 'WHISKY' vs 'WHISKEY' - confirm spelling matches the list exactly.\n\n"
            "Return JSON with ALL fields like:\n"
            '{ "brand": "NATIVE", "class_type": "RYE WHISKY", "abv": "40%", "net_contents": "750 ml" }'
        )

        content_parts = [{"type": "text", "text": user_instructions}]

        if images:
            for blob, mime in images:
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": _b64_data_url(blob, mime)},
                    }
                )

        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": content_parts},
            ],
            temperature=0,
        )

        content = resp.choices[0].message.content.strip()
        print("AI raw response:", content)

        data = json.loads(content)
        
        # Extract all fields
        brand = data.get("brand")
        cls = data.get("class_type")
        abv = data.get("abv")
        net_contents = data.get("net_contents")

        # Normalize empty strings to None
        if brand in ("", None):
            brand = None
        if cls in ("", None):
            cls = None
        if abv in ("", None):
            abv = None
        if net_contents in ("", None):
            net_contents = None
        
        # Return None only if ALL fields are None
        if all(v is None for v in [brand, cls, abv, net_contents]):
            return None

        return {
            "brand": brand,
            "class_type": cls,
            "abv": abv,
            "net_contents": net_contents
        }

    except Exception as e:
        print("AI extraction error:", e)
        return None
