"""
Simple Excel parser - extracts all text from all sheets
"""

import pandas as pd
from typing import Dict


def parse_document(file) -> str:
    """
    Extract all text from Excel file (all sheets, all cells)
    
    Args:
        file: Uploaded Excel file object (from Streamlit)
    
    Returns:
        str: All text content from all sheets
    
    Raises:
        Exception: If file cannot be parsed
    """
    try:
        # Read all sheets
        excel_data = pd.read_excel(file, sheet_name=None, engine='openpyxl')
        
        all_text = []
        
        # Process each sheet
        for sheet_name, df in excel_data.items():
            all_text.append(f"\n=== {sheet_name} ===\n")
            all_text.append(df.to_string(index=False))
        
        return "\n".join(all_text)
        
    except Exception as e:
        raise Exception(f"Error parsing Excel file: {str(e)}")


def get_document_stats(text: str) -> Dict:
    """
    Get statistics about extracted text
    
    Args:
        text: Extracted text string
    
    Returns:
        dict: Statistics (characters, words, estimated pages)
    """
    char_count = len(text)
    word_count = len(text.split())
    estimated_pages = max(1, word_count // 500)
    
    return {
        'total_characters': char_count,
        'total_words': word_count,
        'estimated_pages': estimated_pages
    }