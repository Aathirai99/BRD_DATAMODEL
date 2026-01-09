"""
Test Data Model Generation
Validates the complete pipeline: Parse BRD → Build Prompt → Call Groq → Generate & Validate Data Model
"""

import json
import os
import sys
# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Tuple, List
from dotenv import load_dotenv
from generators import generate_data_model_from_text

load_dotenv()


def validate_data_model_structure(data_model: dict) -> Tuple[bool, List[str]]:
    """
    Validate that the data model has the correct structure
    
    Returns:
        (is_valid, list of errors)
    """
    errors = []
    
    # Check top-level structure
    if not isinstance(data_model, dict):
        errors.append("Data model must be a dictionary/JSON object")
        return False, errors
    
    # Check for required top-level keys
    if "entities" not in data_model:
        errors.append("Missing 'entities' key in data model")
    if "relationships" not in data_model:
        errors.append("Missing 'relationships' key in data model")
    
    # Validate entities
    entities = data_model.get("entities", [])
    if not isinstance(entities, list):
        errors.append("'entities' must be a list")
    else:
        for i, entity in enumerate(entities):
            if not isinstance(entity, dict):
                errors.append(f"Entity {i} must be a dictionary")
                continue
            
            # Check required entity fields
            required_entity_fields = ["name", "type", "description", "fields"]
            for field in required_entity_fields:
                if field not in entity:
                    errors.append(f"Entity {i} missing required field: '{field}'")
            
            # Validate entity type
            entity_type = entity.get("type", "")
            if entity_type not in ["BusinessEntity", "ReferenceEntity"]:
                errors.append(f"Entity {i} has invalid type: '{entity_type}'. Must be 'BusinessEntity' or 'ReferenceEntity'")
            
            # Validate fields
            fields = entity.get("fields", [])
            if not isinstance(fields, list):
                errors.append(f"Entity {i} 'fields' must be a list")
            else:
                for j, field in enumerate(fields):
                    if not isinstance(field, dict):
                        errors.append(f"Entity {i}, Field {j} must be a dictionary")
                        continue
                    
                    # Check required field properties
                    required_field_props = ["name", "dataType", "requirementIds", "sourceRequirements"]
                    for prop in required_field_props:
                        if prop not in field:
                            errors.append(f"Entity {i}, Field {j} missing required property: '{prop}'")
                    
                    # Validate requirementIds is a list
                    req_ids = field.get("requirementIds", [])
                    if not isinstance(req_ids, list):
                        errors.append(f"Entity {i}, Field {j} 'requirementIds' must be a list")
                    
                    # Validate sourceRequirements is a list
                    source_reqs = field.get("sourceRequirements", [])
                    if not isinstance(source_reqs, list):
                        errors.append(f"Entity {i}, Field {j} 'sourceRequirements' must be a list")
    
    # Validate relationships
    relationships = data_model.get("relationships", [])
    if not isinstance(relationships, list):
        errors.append("'relationships' must be a list")
    else:
        for i, rel in enumerate(relationships):
            if not isinstance(rel, dict):
                errors.append(f"Relationship {i} must be a dictionary")
                continue
            
            # Check required relationship fields
            required_rel_fields = ["fromEntity", "toEntity", "relationshipType"]
            for field in required_rel_fields:
                if field not in rel:
                    errors.append(f"Relationship {i} missing required field: '{field}'")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def test_data_model_generation():
    """Test data model generation with a sample BRD"""
    print("=" * 80)
    print("TESTING DATA MODEL GENERATION")
    print("=" * 80)
    
    # Sample BRD for testing
    sample_brd = """
    FR-001: Track customer information including first name, last name, email address, and phone number
    FR-002: Store customer mailing address including street address, city, state, and zip code
    FR-003: Each customer can have multiple phone numbers (mobile, home, work)
    FR-004: Each customer can have multiple addresses (billing, shipping)
    DQR-001: Email addresses must be validated for proper format
    DQR-002: Phone numbers must be validated and standardized
    DQR-003: Zip codes must be validated for US format
    """
    
    try:
        print("\n✅ Step 1: Sample BRD prepared")
        print(f"   BRD length: {len(sample_brd):,} characters")
        
        print("\n✅ Step 2: Generating data model using Groq...")
        print("   This may take 30-60 seconds...")
        
        # Generate data model
        result = generate_data_model_from_text(
            brd_text=sample_brd,
            provider="groq",
            platform="informatica"
        )
        
        print("\n✅ Step 3: Data model generated successfully!")
        print(f"   Model used: {result['model']}")
        print(f"   Provider: {result['provider']}")
        print(f"   Stop reason: {result.get('stop_reason', 'N/A')}")
        print(f"   Token usage:")
        print(f"      Input: {result['usage']['input_tokens']:,}")
        print(f"      Output: {result['usage']['output_tokens']:,}")
        print(f"      Total: {result['usage']['total_tokens']:,}")
        
        # Get data model
        data_model = result['data_model']
        
        print("\n✅ Step 4: Validating data model structure...")
        
        # Validate structure
        is_valid, errors = validate_data_model_structure(data_model)
        
        if is_valid:
            print("   ✅ Data model structure is valid!")
        else:
            print(f"   ❌ Data model structure has {len(errors)} error(s):")
            for error in errors[:10]:  # Show first 10 errors
                print(f"      - {error}")
            if len(errors) > 10:
                print(f"      ... and {len(errors) - 10} more errors")
        
        # Show statistics
        print("\n✅ Step 5: Data Model Statistics")
        entities = data_model.get("entities", [])
        relationships = data_model.get("relationships", [])
        
        print(f"   Entities: {len(entities)}")
        for i, entity in enumerate(entities, 1):
            entity_name = entity.get("name", "Unknown")
            entity_type = entity.get("type", "Unknown")
            field_count = len(entity.get("fields", []))
            print(f"      {i}. {entity_name} ({entity_type}): {field_count} fields")
        
        print(f"   Relationships: {len(relationships)}")
        for i, rel in enumerate(relationships, 1):
            from_entity = rel.get("fromEntity", "Unknown")
            to_entity = rel.get("toEntity", "Unknown")
            rel_type = rel.get("relationshipType", "Unknown")
            print(f"      {i}. {from_entity} --{rel_type}--> {to_entity}")
        
        # Show sample entity details
        if entities:
            print("\n✅ Step 6: Sample Entity Details")
            sample_entity = entities[0]
            print(f"   Entity: {sample_entity.get('name', 'Unknown')}")
            print(f"   Type: {sample_entity.get('type', 'Unknown')}")
            print(f"   Description: {sample_entity.get('description', 'N/A')[:100]}...")
            
            fields = sample_entity.get("fields", [])
            if fields:
                print(f"\n   First {min(5, len(fields))} fields:")
                for i, field in enumerate(fields[:5], 1):
                    field_name = field.get("name", "Unknown")
                    data_type = field.get("dataType", "Unknown")
                    req_ids = field.get("requirementIds", [])
                    is_custom = field.get("isCustom", False)
                    print(f"      {i}. {field_name} ({data_type})")
                    print(f"         Requirement IDs: {req_ids}")
                    print(f"         Custom: {is_custom}")
        
        # Show full JSON (first 2000 chars)
        print("\n✅ Step 7: Generated JSON (preview - first 2000 chars)")
        print("-" * 80)
        json_str = json.dumps(data_model, indent=2)
        print(json_str[:2000])
        if len(json_str) > 2000:
            print("\n...")
            print("(JSON truncated for display)")
        print("-" * 80)
        
        # Save to file
        output_file = "generated_data_model.json"
        print(f"\n✅ Step 8: Saving to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(data_model, f, indent=2)
        print(f"   ✅ Saved to {output_file}")
        
        # Final summary
        print("\n" + "=" * 80)
        if is_valid:
            print("✅ DATA MODEL GENERATION TEST PASSED!")
            print("   The generated data model has a valid structure.")
        else:
            print("⚠️  DATA MODEL GENERATION TEST COMPLETED WITH WARNINGS")
            print(f"   Found {len(errors)} validation error(s).")
            print("   Review the errors above and check the generated JSON.")
        print("=" * 80)
        
        return is_valid
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_data_model_generation()
    exit(0 if success else 1)

