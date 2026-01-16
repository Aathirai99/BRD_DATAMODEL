"""
Modular Pipeline: BRD Excel → Parse → Prompt → Cursor AI → JSON → Visualizations

Each step is a separate, reusable function that Cursor can call independently.
This allows for iterative refinement and selective re-execution of specific steps.
"""

import os
import sys
import glob
from pathlib import Path
from parsers import parse_document
from cursor_workflow import save_prompt_to_file, parse_cursor_response
from generators import save_drawio_file, generate_html_report


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def find_excel_files(directory="."):
    """
    Find all Excel files (.xlsx) in the specified directory
    
    Args:
        directory: Directory to search (default: current directory)
    
    Returns:
        List of Excel file paths
    """
    excel_files = glob.glob(os.path.join(directory, "*.xlsx"))
    # Filter out files in outputs directory
    excel_files = [f for f in excel_files if "outputs" not in f]
    return excel_files


def get_output_filename(brd_file_path):
    """
    Generate output filenames based on BRD filename
    
    Args:
        brd_file_path: Path to BRD Excel file
    
    Returns:
        Dictionary with output file paths
    """
    brd_name = Path(brd_file_path).stem  # Get filename without extension
    # Clean filename (remove spaces, special chars)
    clean_name = brd_name.lower().replace(" ", "_").replace("-", "_")
    
    return {
        'prompt': f"outputs/{clean_name}_prompt.txt",
        'json': f"outputs/{clean_name}_response.json",
        'drawio': f"outputs/{clean_name}_data_model.drawio",
        'html': f"outputs/{clean_name}_data_model_report.html"
    }


def ensure_outputs_directory():
    """Create outputs directory if it doesn't exist"""
    os.makedirs("outputs", exist_ok=True)


# ============================================================================
# MODULAR STEP FUNCTIONS (Each can be called independently)
# ============================================================================

def step1_parse_brd(brd_file_path=None):
    """
    STEP 1: Parse Excel BRD file and extract text
    
    This function:
    - Finds Excel file (auto-detects if not provided)
    - Parses all sheets and extracts text
    - Returns BRD text and output file paths
    
    Args:
        brd_file_path: Path to BRD Excel file (auto-detects if None)
    
    Returns:
        tuple: (brd_text, outputs_dict) or (None, None) if error
    
    Usage:
        brd_text, outputs = step1_parse_brd()
        # or
        brd_text, outputs = step1_parse_brd("path/to/brd.xlsx")
    """
    print("=" * 70)
    print("STEP 1: Parsing BRD Excel File")
    print("=" * 70)
    
    # Find Excel file
    if brd_file_path is None:
        excel_files = find_excel_files()
        if not excel_files:
            print("❌ No Excel files found in current directory!")
            return None, None
        
        if len(excel_files) > 1:
            print(f"⚠️  Found {len(excel_files)} Excel files, using first: {excel_files[0]}")
        
        brd_file_path = excel_files[0]
    
    if not os.path.exists(brd_file_path):
        print(f"❌ File not found: {brd_file_path}")
        return None, None
    
    print(f"📄 BRD File: {brd_file_path}")
    
    # Generate output filenames
    outputs = get_output_filename(brd_file_path)
    ensure_outputs_directory()
    
    # Parse BRD
    try:
        with open(brd_file_path, 'rb') as f:
            brd_text = parse_document(f)
        
        print(f"✅ Successfully parsed BRD")
        print(f"   📊 Extracted {len(brd_text):,} characters")
        print(f"   📊 Approximately {len(brd_text.split()):,} words")
        print()
        
        return brd_text, outputs
        
    except Exception as e:
        print(f"❌ Error parsing BRD: {str(e)}")
        return None, None


def step2_generate_prompt(brd_text, outputs):
    """
    STEP 2: Generate Cursor AI prompt from BRD text
    
    This function:
    - Takes parsed BRD text
    - Generates formatted prompt for Cursor AI
    - Saves prompt to file
    
    Args:
        brd_text: Parsed BRD text from step1_parse_brd()
        outputs: Output file paths dict from step1_parse_brd()
    
    Returns:
        str: Path to prompt file, or None if error
    
    Usage:
        prompt_path = step2_generate_prompt(brd_text, outputs)
    """
    print("=" * 70)
    print("STEP 2: Generating Cursor AI Prompt")
    print("=" * 70)
    
    if not brd_text:
        print("❌ No BRD text provided!")
        return None
    
    try:
        save_prompt_to_file(brd_text, outputs['prompt'])
        print(f"✅ Prompt saved to: {outputs['prompt']}")
        print()
        return outputs['prompt']
        
    except Exception as e:
        print(f"❌ Error generating prompt: {str(e)}")
        return None


def step3_cursor_instructions(outputs):
    """
    STEP 3: Display instructions for Cursor AI processing
    
    This is a manual step - Cursor AI needs to process the prompt.
    This function just shows what to do next.
    
    Args:
        outputs: Output file paths dict
    
    Returns:
        str: Instructions text
    """
    print("=" * 70)
    print("STEP 3: Cursor AI Processing (Manual Step)")
    print("=" * 70)
    print("📋 Instructions for Cursor AI:")
    print(f"   1. Read the prompt file: {outputs['prompt']}")
    print(f"   2. Generate the data model JSON following the prompt")
    print(f"   3. Save the JSON response to: {outputs['json']}")
    print()
    print("💡 To have Cursor do this automatically, say:")
    print(f"   'Read {outputs['prompt']} and generate the data model JSON.'")
    print(f"   'Save the JSON to {outputs['json']}'")
    print()
    return outputs['json']


def step4_generate_visualizations(json_path=None, outputs=None):
    """
    STEP 4: Generate Draw.io and HTML visualizations from JSON
    
    This function:
    - Loads JSON data model
    - Generates Draw.io diagram
    - Generates HTML report
    
    Args:
        json_path: Path to JSON file (auto-detects if None)
        outputs: Output file paths dict (auto-generates if None)
    
    Returns:
        tuple: (drawio_path, html_path) or (None, None) if error
    
    Usage:
        drawio, html = step4_generate_visualizations()
        # or
        drawio, html = step4_generate_visualizations("outputs/response.json")
    """
    print("=" * 70)
    print("STEP 4: Generating Visualizations")
    print("=" * 70)
    
    # Auto-detect JSON if not provided
    if json_path is None:
        # Try to find JSON in outputs
        json_files = glob.glob("outputs/*_response.json")
        if not json_files:
            print("❌ No JSON response file found!")
            print("   Please ensure Cursor has generated the JSON first.")
            return None, None
        
        if len(json_files) > 1:
            print(f"⚠️  Found {len(json_files)} JSON files, using first: {json_files[0]}")
        
        json_path = json_files[0]
    
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return None, None
    
    # Auto-generate output paths if not provided
    if outputs is None:
        # Infer from JSON filename
        json_name = Path(json_path).stem.replace("_response", "")
        outputs = {
            'drawio': f"outputs/{json_name}_data_model.drawio",
            'html': f"outputs/{json_name}_data_model_report.html"
        }
    
    print(f"📄 JSON File: {json_path}")
    
    try:
        # Parse JSON
        print("   Loading JSON data model...")
        data_model = parse_cursor_response(json_path)
        
        # Generate Draw.io
        print("   Generating Draw.io diagram...")
        save_drawio_file(data_model, outputs['drawio'])
        print(f"   ✅ Draw.io saved: {outputs['drawio']}")
        
        # Generate HTML report
        print("   Generating HTML report...")
        generate_html_report(data_model, outputs['html'])
        print(f"   ✅ HTML report saved: {outputs['html']}")
        print()
        
        return outputs['drawio'], outputs['html']
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {str(e)}")
        return None, None


# ============================================================================
# ORCHESTRATOR FUNCTIONS
# ============================================================================

def run_full_pipeline(brd_file_path=None):
    """
    Run the complete pipeline: Parse → Prompt → (Cursor) → Visualizations
    
    This orchestrates all steps. Individual steps can be called separately
    for iterative refinement.
    
    Args:
        brd_file_path: Path to BRD Excel file (auto-detects if None)
    
    Returns:
        bool: True if successful
    """
    print("=" * 70)
    print("🚀 BRD to Data Model - Full Pipeline")
    print("=" * 70)
    print()
    
    # Step 1: Parse BRD
    brd_text, outputs = step1_parse_brd(brd_file_path)
    if not brd_text:
        return False
    
    # Step 2: Generate prompt
    prompt_path = step2_generate_prompt(brd_text, outputs)
    if not prompt_path:
        return False
    
    # Step 3: Instructions for Cursor
    json_path = step3_cursor_instructions(outputs)
    
    # Step 4: Check if JSON exists and generate visualizations
    if os.path.exists(json_path):
        print("✅ Found existing JSON response!")
        drawio, html = step4_generate_visualizations(json_path, outputs)
        if drawio and html:
            print("=" * 70)
            print("✅ PIPELINE COMPLETE!")
            print("=" * 70)
            print("\n📁 Generated Files:")
            print(f"   1. {outputs['prompt']} - Cursor prompt")
            print(f"   2. {json_path} - Data model JSON")
            print(f"   3. {drawio} - Draw.io diagram")
            print(f"   4. {html} - HTML report")
            print("\n🎉 Open the HTML report in your browser to view the data model!")
            return True
    else:
        print("\n⏳ Waiting for Cursor to generate JSON...")
        print("   After Cursor generates the JSON, run:")
        print("   - step4_generate_visualizations()")
        print("   - OR: python run_full_pipeline.py --visuals-only")
        return True


def regenerate_step(step_name, **kwargs):
    """
    Regenerate a specific step (for iterative refinement)
    
    Args:
        step_name: Name of step to regenerate
                  Options: 'parse', 'prompt', 'visualizations'
        **kwargs: Additional arguments for the step
    
    Returns:
        Result of the step function
    """
    if step_name == 'parse':
        return step1_parse_brd(kwargs.get('brd_file_path'))
    
    elif step_name == 'prompt':
        brd_text = kwargs.get('brd_text')
        outputs = kwargs.get('outputs')
        if not brd_text or not outputs:
            # Re-run parse first
            brd_text, outputs = step1_parse_brd()
        return step2_generate_prompt(brd_text, outputs)
    
    elif step_name == 'visualizations':
        return step4_generate_visualizations(
            kwargs.get('json_path'),
            kwargs.get('outputs')
        )
    
    else:
        print(f"❌ Unknown step: {step_name}")
        print("   Available steps: 'parse', 'prompt', 'visualizations'")
        return None


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point with command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Modular pipeline: BRD Excel → Parse → Prompt → Cursor AI → JSON → Visualizations"
    )
    parser.add_argument(
        '--brd',
        type=str,
        help='Path to BRD Excel file (auto-detects if not provided)'
    )
    parser.add_argument(
        '--step',
        type=str,
        choices=['parse', 'prompt', 'visualizations', 'all'],
        default='all',
        help='Run specific step only (default: all)'
    )
    parser.add_argument(
        '--visuals-only',
        action='store_true',
        help='Only generate visualizations (skip parsing and prompt generation)'
    )
    
    args = parser.parse_args()
    
    if args.visuals_only or args.step == 'visualizations':
        # Only generate visualizations
        drawio, html = step4_generate_visualizations()
        if drawio and html:
            print(f"\n✅ Visualizations generated!")
            print(f"   - {drawio}")
            print(f"   - {html}")
            return 0
        return 1
    
    if args.step == 'parse':
        brd_text, outputs = step1_parse_brd(args.brd)
        return 0 if brd_text else 1
    
    if args.step == 'prompt':
        brd_text, outputs = step1_parse_brd(args.brd)
        if brd_text:
            step2_generate_prompt(brd_text, outputs)
            return 0
        return 1
    
    # Default: run full pipeline
    success = run_full_pipeline(args.brd)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
