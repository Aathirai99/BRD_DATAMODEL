"""
Cursor AI Workflow Helper
Generates formatted prompts to copy-paste into Cursor
"""

import json
from prompts import INFORMATICA_SYSTEM_PROMPT, build_prompt


def generate_cursor_prompt(brd_text, platform="informatica"):
    """
    Generate a complete prompt for Cursor AI
    
    Args:
        brd_text: Extracted FRD text
        platform: Target platform (informatica or snowflake)
    
    Returns:
        Complete prompt string to copy-paste into Cursor
    """
    
    system_prompt, user_prompt = build_prompt(brd_text, platform)
    
    # CRITICAL: Lock Cursor into output-only mode
    cursor_constraint = """
╔════════════════════════════════════════════════════════════╗
║  CRITICAL: YOU ARE IN OUTPUT-ONLY MODE                    ║
╚════════════════════════════════════════════════════════════╝

YOUR ONLY JOB: Generate a JSON data model

YOU CANNOT:
❌ Edit any Python files
❌ Suggest code changes  
❌ Modify prompts.py
❌ Touch parsers.py
❌ Change any .py files

YOU CAN ONLY:
✅ Read the FRD below
✅ Follow the Informatica rules below
✅ Output valid JSON data model
✅ Nothing else

If you see issues: FIX THE JSON OUTPUT, not the code.

Your response must be ONLY JSON starting with { and ending with }

════════════════════════════════════════════════════════════

"""
    
    # Combine: Constraint + System Prompt + BRD + Instructions
    cursor_prompt = f"""{cursor_constraint}
{system_prompt}

===== FRD TO ANALYZE =====

{brd_text}

===== INSTRUCTIONS =====

Generate the data model following all rules and examples provided above.
Return ONLY valid JSON with no markdown code blocks, no preamble, no explanation.
Start with {{ and end with }}.
"""
    
    return cursor_prompt


def save_prompt_to_file(brd_text, output_path="cursor_prompt.txt", platform="informatica"):
    """
    Save the Cursor prompt to a text file
    
    Args:
        brd_text: Extracted FRD text
        output_path: Where to save the prompt file
        platform: Target platform
    """
    
    prompt = generate_cursor_prompt(brd_text, platform)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"✅ Prompt saved to: {output_path}")
    print(f"📋 Prompt length: {len(prompt):,} characters")
    print(f"\nNext steps:")
    print(f"1. Open {output_path}")
    print(f"2. Copy entire contents")
    print(f"3. Open Cursor AI chat (Cmd/Ctrl + L)")
    print(f"4. Paste and send")
    print(f"5. Copy the JSON response")
    print(f"6. Save as 'cursor_response.json'")


def parse_cursor_response(response_path="outputs/test_cursor_response.json"):
    """
    Load and validate the JSON response from Cursor
    
    Args:
        response_path: Path to Cursor's JSON response
    
    Returns:
        Parsed data model dictionary
    
    Raises:
        Exception if JSON is invalid
    """
    
    try:
        with open(response_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Clean up if Cursor included markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Parse JSON
        data_model = json.loads(content)
        
        # Validate structure
        if "dataModel" not in data_model:
            raise ValueError("Response missing 'dataModel' key")
        
        print("✅ Valid data model loaded!")
        print(f"📊 Found {len(data_model['dataModel']['entities'])} entities")
        
        return data_model
        
    except FileNotFoundError:
        raise Exception(f"File not found: {response_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")


def validate_data_model(data_model):
    """
    Validate that data model has correct structure
    
    Args:
        data_model: Dictionary to validate
    
    Returns:
        bool: True if valid
    
    Raises:
        ValueError: If validation fails
    """
    
    # Check required keys
    if "metadata" not in data_model:
        raise ValueError("Missing 'metadata' key in data model")
    
    if "reasoning" not in data_model:
        raise ValueError("Missing 'reasoning' key in data model")
    
    if "dataModel" not in data_model:
        raise ValueError("Missing 'dataModel' key in data model")
    
    if "entities" not in data_model["dataModel"]:
        raise ValueError("Missing 'entities' key in dataModel")
    
    if not isinstance(data_model["dataModel"]["entities"], list):
        raise ValueError("'entities' must be a list")
    
    # Validate each entity
    for i, entity in enumerate(data_model["dataModel"]["entities"]):
        if "name" not in entity:
            raise ValueError(f"Entity {i} missing 'name' key")
        if "type" not in entity:
            raise ValueError(f"Entity '{entity['name']}' missing 'type' key")
        if "fields" not in entity:
            raise ValueError(f"Entity '{entity['name']}' missing 'fields' key")
        
        # Validate fields
        for j, field in enumerate(entity["fields"]):
            if "name" not in field:
                raise ValueError(f"Entity '{entity['name']}' field {j} missing 'name' key")
            if "dataType" not in field:
                raise ValueError(f"Field '{field.get('name')}' missing 'dataType' key")
    
    return True


# Quick test function
def test_workflow():
    """Test the workflow with a simple FRD"""
    
    test_brd = """
    We need to track customer information including:
    - Customer first and last name
    - Email address
    - Phone number
    """
    
    print("=" * 60)
    print("CURSOR WORKFLOW TEST")
    print("=" * 60)
    
    # Generate prompt
    print("\n1. Generating Cursor prompt...")
    save_prompt_to_file(test_brd, "test_cursor_prompt.txt")
    
    print("\n2. Now manually:")
    print("   - Open test_cursor_prompt.txt")
    print("   - Copy contents")
    print("   - Paste into Cursor AI")
    print("   - Save Cursor's JSON response as test_cursor_response.json")
    print("   - Then run: parse_cursor_response('test_cursor_response.json')")


if __name__ == "__main__":
    test_workflow()