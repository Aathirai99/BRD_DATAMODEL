"""
Phase 3 Tester - Validate Prompts
Tests the prompt building without calling Claude API
"""

import sys
import os
# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts import build_prompt, INFORMATICA_SYSTEM_PROMPT

def test_phase_3():
    print("=" * 80)
    print("PHASE 3 VALIDATION - PROMPT TESTING")
    print("=" * 80)
    
    # Test 1: Check prompt module loads
    print("\n✅ TEST 1: Prompt module imports successfully")
    
    # Test 2: Check system prompt exists
    print("\n✅ TEST 2: System prompt loaded")
    print(f"   System prompt length: {len(INFORMATICA_SYSTEM_PROMPT):,} characters")
    
    # Test 3: Build prompt with sample BRD
    print("\n✅ TEST 3: Building prompt with sample BRD")
    sample_brd = """
    FR-001: Track customer information including name, email, and phone number
    FR-002: Store customer mailing address
    DQR-001: Email addresses must be validated for format
    """
    
    system_prompt, user_prompt = build_prompt(sample_brd)
    
    print(f"   System prompt: {len(system_prompt):,} characters")
    print(f"   User prompt: {len(user_prompt):,} characters")
    
    # Test 4: Verify key elements in system prompt
    print("\n✅ TEST 4: Checking critical elements in system prompt")
    
    checks = {
        "JSON format example": '"entities":' in system_prompt,
        "Traceability fields": '"requirementIds"' in system_prompt,
        "Field groups": 'PostalAddress' in system_prompt,
        "Data types": 'TextField' in system_prompt,
        "Meta fields": '_meta' in system_prompt
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    # Test 5: Preview system prompt sections
    print("\n✅ TEST 5: System prompt preview (first 500 chars)")
    print("-" * 80)
    print(system_prompt[:500])
    print("...")
    print("-" * 80)
    
    # Test 6: Preview user prompt
    print("\n✅ TEST 6: User prompt preview")
    print("-" * 80)
    print(user_prompt)
    print("-" * 80)
    
    # Final summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ PHASE 3 COMPLETE! All checks passed.")
        print("\nYour prompt is ready to use with Claude API!")
        print("\nNext step: Phase 4 - Claude Integration")
    else:
        print("❌ PHASE 3 INCOMPLETE - Some checks failed")
        print("Please review the prompt structure")
    print("=" * 80)


def test_with_usf_file():
    """
    Test with actual USF BRD file
    """
    print("\n" + "=" * 80)
    print("BONUS TEST: With Real USF BRD File")
    print("=" * 80)
    
    try:
        from parsers import parse_document
        
        file_path = "/Users/aathirai_s_t/Downloads/POC3_EXP/brd-datamodel-core/USF Requirements Document - Phase 0B.xlsx"
        
        with open(file_path, 'rb') as f:
            print("\n📄 Parsing USF BRD...")
            brd_text = parse_document(f)
            
            print(f"✅ Parsed: {len(brd_text):,} characters")
            
            print("\n📝 Building prompt with USF BRD...")
            system_prompt, user_prompt = build_prompt(brd_text)
            
            print(f"✅ System prompt: {len(system_prompt):,} characters")
            print(f"✅ User prompt: {len(user_prompt):,} characters")
            
            # Show snippet of user prompt with BRD
            print("\n📖 User prompt preview (first 800 chars):")
            print("-" * 80)
            print(user_prompt[:800])
            print("...")
            print("-" * 80)
            
            print("\n✅ Prompt ready for USF BRD!")
            print("   This will be sent to Claude API in Phase 4")
            
    except FileNotFoundError:
        print("\n⚠️  USF file not found at expected location")
        print("   This is OK - you can test with your own file later")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Run main tests
    test_phase_3()
    
    # Try with real file
    print("\n")
    test_with_usf_file()
    
    print("\n" + "=" * 80)
    print("PHASE 3 TESTING COMPLETE!")
    print("=" * 80)
    print("\nIf all tests passed, you're ready for Phase 4!")
    print("Run: python test_phase3.py")

