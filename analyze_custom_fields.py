"""
Helper script to identify explicit custom fields from FRD requirements
This helps ensure all explicit custom fields are identified before generating the data model
"""

import pandas as pd
import re
from pathlib import Path


def load_ootb_field_names():
    """Load all OOTB Person field names from the catalog"""
    ootb_fields = set()
    
    # Try to load from ootb_person_reference.txt
    candidates = [
        Path('ootb_person_reference.txt'),
        Path(__file__).resolve().parent.parent / 'ootb_person_reference.txt',
    ]
    
    ootb_text = ""
    for path in candidates:
        if path.exists():
            try:
                ootb_text = path.read_text(encoding='utf-8')
                break
            except Exception:
                pass
    
    if not ootb_text:
        print("⚠️  Warning: Could not load OOTB catalog")
        return ootb_fields
    
    # Extract field names from catalog (format: "- Field Name (fieldName)")
    pattern = r'- [^(]+\((\w+)\)'
    matches = re.findall(pattern, ootb_text)
    ootb_fields.update(matches)
    
    # Also extract from field group descriptions
    pattern2 = r'(\w+)\s*\[(?:Text|Lookup|Date|Boolean|Integer|Double|Clob)'
    matches2 = re.findall(pattern2, ootb_text)
    ootb_fields.update(matches2)
    
    return ootb_fields


def extract_explicit_fields_from_frd(excel_path):
    """Extract explicit field mentions from FRD requirements"""
    excel_data = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
    
    if 'Functional Requirements' not in excel_data:
        return []
    
    df = excel_data['Functional Requirements']
    explicit_fields = []
    
    # Common patterns for explicit field mentions
    field_patterns = [
        r'\b(CWID|cwid|CWID)\b',
        r'\b(PIDM|pidm|PIDM)\b',
        r'\b(Classification|classification)\b',
        r'source\s+(?:system\s+)?(?:address|phone|email)\s+id',
        r'unique\s+(?:primary\s+)?key\s+(?:value\s+)?for\s+(?:each\s+)?(address|phone|email)',
        r'constituent\s+(?:type|role)',
        r'employee\s+classification',
    ]
    
    for idx, row in df.iterrows():
        fr_num = row.get('FR #', '')
        desc = str(row.get('Functional Requirements Description', ''))
        
        if pd.isna(fr_num) or pd.isna(desc):
            continue
        
        # Check for explicit field mentions
        for pattern in field_patterns:
            matches = re.finditer(pattern, desc, re.IGNORECASE)
            for match in matches:
                field_context = desc[max(0, match.start()-50):match.end()+50]
                explicit_fields.append({
                    'requirementId': str(fr_num),
                    'fieldMention': match.group(),
                    'context': field_context.strip(),
                    'fullRequirement': desc[:200]
                })
    
    return explicit_fields


def identify_custom_fields(excel_path):
    """Identify which explicit fields should be custom (not in OOTB)"""
    print("=" * 70)
    print("ANALYZING FRD FOR EXPLICIT CUSTOM FIELDS")
    print("=" * 70)
    print()
    
    # Load OOTB fields
    print("📚 Loading OOTB Person entity field catalog...")
    ootb_fields = load_ootb_field_names()
    print(f"   Found {len(ootb_fields)} OOTB fields")
    print()
    
    # Extract explicit fields from FRD
    print("🔍 Scanning FRD requirements for explicit field mentions...")
    explicit_fields = extract_explicit_fields_from_frd(excel_path)
    print(f"   Found {len(explicit_fields)} explicit field mentions")
    print()
    
    # Identify custom fields
    print("🎯 Identifying custom fields (not in OOTB)...")
    print()
    
    custom_fields = []
    for field_info in explicit_fields:
        field_name = field_info['fieldMention'].lower()
        
        # Map mentions to actual field names
        field_mapping = {
            'cwid': 'cwid',
            'pidm': 'pidm',
            'classification': 'classification',
            'address': 'sourceAddressId',
            'phone': 'sourcePhoneId',
            'email': 'sourceEmailId',
        }
        
        actual_field_name = None
        for key, value in field_mapping.items():
            if key in field_name:
                actual_field_name = value
                break
        
        if actual_field_name and actual_field_name not in ootb_fields:
            custom_fields.append({
                'fieldName': actual_field_name,
                'requirementId': field_info['requirementId'],
                'context': field_info['context'],
                'fullRequirement': field_info['fullRequirement']
            })
            print(f"   ✅ {actual_field_name:25} (FR{field_info['requirementId']}) - CUSTOM FIELD REQUIRED")
            print(f"      Context: {field_info['context'][:80]}...")
        elif actual_field_name:
            print(f"   ℹ️  {actual_field_name:25} (FR{field_info['requirementId']}) - Found in OOTB")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total explicit field mentions: {len(explicit_fields)}")
    print(f"Custom fields required: {len(custom_fields)}")
    print()
    
    if custom_fields:
        print("📋 Custom fields that MUST be included in data model:")
        for cf in custom_fields:
            print(f"   - {cf['fieldName']} (FR{cf['requirementId']})")
    else:
        print("✅ No explicit custom fields identified")
    
    print()
    return custom_fields


if __name__ == "__main__":
    import sys
    
    excel_path = sys.argv[1] if len(sys.argv) > 1 else "USF Requirements Document Cleaned.xlsx"
    
    if not Path(excel_path).exists():
        print(f"❌ Error: File not found: {excel_path}")
        sys.exit(1)
    
    custom_fields = identify_custom_fields(excel_path)
    
    if custom_fields:
        print("\n💡 TIP: Ensure these custom fields are included when generating the data model JSON")
        print("   Set isCustom: true for all of these fields")
