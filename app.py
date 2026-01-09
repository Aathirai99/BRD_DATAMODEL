"""
Main application entry point
BRD to Data Model Generator using Cursor-based analysis
"""

from run_full_pipeline import run_full_pipeline

if __name__ == "__main__":
    import sys
    
    # Default BRD file
    brd_file = "USF Requirements Document Cleaned.xlsx"
    
    if len(sys.argv) > 1:
        brd_file = sys.argv[1]
    
    success = run_full_pipeline(brd_file_path=brd_file)
    sys.exit(0 if success else 1)

