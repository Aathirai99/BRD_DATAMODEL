"""
Test the parser with the USF BRD file
"""

import sys
import os
# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers import parse_document, get_document_stats

def test_with_usf_file():
    print("=" * 80)
    print("TESTING PARSER WITH USF BRD")
    print("=" * 80)
    
    file_path = "/Users/aathirai_s_t/Downloads/POC3_EXP/brd-datamodel-core/USF Requirements Document - Phase 0B.xlsx"
    
    try:
        # Open and parse
        with open(file_path, 'rb') as f:
            print("\n📄 Parsing USF BRD Excel file...")
            text = parse_document(f)
            
            # Get stats
            stats = get_document_stats(text)
            
            print(f"\n✅ Parsed successfully!")
            print(f"   Characters: {stats['total_characters']:,}")
            print(f"   Words: {stats['total_words']:,}")
            print(f"   Estimated Pages: {stats['estimated_pages']}")
            
            # Show preview
            print(f"\n📖 Content Preview (first 1000 chars):")
            print("-" * 80)
            print(text[:1000])
            print("...")
            print("-" * 80)
            
            # Show last part too
            print(f"\n📖 Content End Preview (last 500 chars):")
            print("-" * 80)
            print("...")
            print(text[-500:])
            print("-" * 80)
            
            print("\n✅ PHASE 2 COMPLETE! Parser works!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_with_usf_file()

