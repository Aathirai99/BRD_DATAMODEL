"""
Run the complete pipeline: Parse BRD → Generate Data Model (Cursor-based) → Generate Report
"""

import json
import os
from generate_data_model_manual import generate_data_model_from_brd
from generate_data_model_report import generate_html_report

def run_full_pipeline(
    brd_file_path: str,
    output_json: str = "generated_data_model.json",
    output_report: str = "data_model_report.html"
):
    """
    Run the complete pipeline from BRD to HTML report using Cursor-based generation
    
    Args:
        brd_file_path: Path to BRD Excel file
        output_json: Output JSON file path
        output_report: Output HTML report path
    """
    print("=" * 80)
    print("BRD TO DATA MODEL PIPELINE (Cursor-based)")
    print("=" * 80)
    
    # Step 1: Check if file exists
    if not os.path.exists(brd_file_path):
        print(f"\n❌ Error: BRD file not found: {brd_file_path}")
        return False
    
    print(f"\n✅ Step 1: BRD file found")
    print(f"   File: {brd_file_path}")
    file_size = os.path.getsize(brd_file_path) / 1024  # KB
    print(f"   Size: {file_size:.1f} KB")
    
    # Step 2: Generate data model using Cursor-based approach
    print(f"\n✅ Step 2: Generating data model using Cursor AI analysis...")
    print("   Analyzing BRD and extracting requirements...")
    
    try:
        # Generate data model
        data_model = generate_data_model_from_brd(brd_file_path)
        
        print(f"\n✅ Step 3: Data model generated successfully!")
        
        # Step 4: Save JSON
        print(f"\n✅ Step 4: Saving data model to {output_json}...")
        with open(output_json, 'w') as f:
            json.dump(data_model, f, indent=2)
        print(f"   ✅ Saved successfully!")
        
        # Step 5: Generate HTML report
        print(f"\n✅ Step 5: Generating HTML report...")
        generate_html_report(data_model, output_report)
        print(f"   ✅ Report saved to {output_report}")
        
        # Summary
        entities = data_model.get('entities', [])
        business_entities = [e for e in entities if e.get('type') == 'BusinessEntity']
        total_fields = sum(len(e.get('fields', [])) for e in business_entities)
        
        print("\n" + "=" * 80)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Business Entities: {len(business_entities)}")
        print(f"   Reference Entities: {len(entities) - len(business_entities)}")
        print(f"   Total Fields: {total_fields}")
        print(f"   Relationships: {len(data_model.get('relationships', []))}")
        print(f"   Data Model: {output_json}")
        print(f"   HTML Report: {output_report}")
        print("\n✅ All done! Open the HTML report to view the results.")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    # Default BRD file path
    brd_file = "USF Requirements Document - Phase 0B.xlsx"
    
    # Allow override via command line
    if len(sys.argv) > 1:
        brd_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(brd_file):
        print(f"❌ Error: BRD file not found: {brd_file}")
        print(f"\nUsage: python run_full_pipeline.py [path_to_brd_file.xlsx]")
        sys.exit(1)
    
    # Run pipeline
    success = run_full_pipeline(
        brd_file_path=brd_file
    )
    
    sys.exit(0 if success else 1)

