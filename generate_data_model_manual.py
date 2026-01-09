"""
Manually generate data model from BRD using Cursor AI
Analyzes the BRD and creates Informatica MDM data model JSON
"""

import json
import re
import pandas as pd
from parsers import parse_document
from prompts import build_prompt

def extract_requirements(brd_file_path):
    """Extract requirement IDs and their full descriptions from Excel"""
    requirements = {}
    
    # Read Excel directly to get structured data
    try:
        excel_data = pd.read_excel(brd_file_path, sheet_name=None, engine='openpyxl')
        
        # Look for Functional Requirements sheet
        for sheet_name, df in excel_data.items():
            if 'functional' in sheet_name.lower() or 'requirement' in sheet_name.lower():
                # Check if we have FR # column
                if 'FR #' in df.columns or 'FR#' in df.columns:
                    fr_col = 'FR #' if 'FR #' in df.columns else 'FR#'
                    desc_col = None
                    for col in df.columns:
                        if 'description' in col.lower() or 'requirement' in col.lower():
                            desc_col = col
                            break
                    
                    if desc_col:
                        for idx, row in df.iterrows():
                            fr_val = row.get(fr_col)
                            if pd.notna(fr_val):
                                # Extract FR number
                                fr_match = re.search(r'FR\s*(\d+)', str(fr_val), re.IGNORECASE)
                                if fr_match:
                                    req_id = f"FR-{fr_match.group(1)}"
                                    desc = str(row.get(desc_col, ''))
                                    
                                    # Also get comments if available
                                    comments = ''
                                    if 'Comments' in df.columns:
                                        comments_val = row.get('Comments', '')
                                        if pd.notna(comments_val):
                                            comments = str(comments_val)
                                    
                                    # Combine description and comments
                                    full_desc = desc
                                    if comments and comments.strip():
                                        full_desc = f"{desc} {comments}".strip()
                                    
                                    # Clean up - remove extra whitespace
                                    full_desc = re.sub(r'\s+', ' ', full_desc)
                                    
                                    # Keep the longest/most complete description
                                    if req_id not in requirements or len(full_desc) > len(requirements.get(req_id, "")):
                                        requirements[req_id] = full_desc
                
                # Check for DQR requirements
                if 'DQR' in df.to_string():
                    for idx, row in df.iterrows():
                        for col in df.columns:
                            val = row.get(col)
                            if pd.notna(val) and 'DQR' in str(val).upper():
                                dqr_match = re.search(r'DQR\s*(\d+)', str(val), re.IGNORECASE)
                                if dqr_match:
                                    req_id = f"DQR-{dqr_match.group(1)}"
                                    # Try to find description
                                    desc = ''
                                    for desc_col in df.columns:
                                        if 'description' in desc_col.lower():
                                            desc_val = row.get(desc_col, '')
                                            if pd.notna(desc_val):
                                                desc = str(desc_val)
                                                break
                                    if desc:
                                        requirements[req_id] = desc
    
    except Exception as e:
        print(f"Warning: Could not extract requirements from Excel structure: {e}")
        # Fallback to text-based extraction
        with open(brd_file_path, 'rb') as f:
            brd_text = parse_document(f)
        
        # Simple text-based extraction as fallback
        fr_pattern = r'FR(\d+)[^\d]*?([^\n]{100,500})'
        for match in re.finditer(fr_pattern, brd_text, re.IGNORECASE):
            req_id = f"FR-{match.group(1)}"
            desc = match.group(2).strip()
            if req_id not in requirements:
                requirements[req_id] = desc
    
    return requirements

def build_source_requirement_text(req_id, requirements_dict):
    """Build full requirement text from requirement ID"""
    if req_id == "STANDARD":
        return "Standard meta field - required for all entities"
    
    if req_id in requirements_dict:
        full_text = requirements_dict[req_id]
        # Format as "FR-10: Full description text"
        return f"{req_id}: {full_text}"
    else:
        # Fallback to short description
        return f"{req_id}: Requirement description not found in BRD"

def build_field_reasoning(field_name, field_description, requirement_ids, requirements_dict):
    """Build reasoning dictionary for all requirements mapped to a field"""
    reasoning_dict = {}
    for req_id in requirement_ids:
        req_text = requirements_dict.get(req_id, "")
        reasoning = analyze_requirement_for_fields(req_id, req_text, field_name, field_description)
        reasoning_dict[req_id] = reasoning
    return reasoning_dict

def analyze_requirement_for_fields(req_id, req_text, field_name, field_description):
    """Analyze requirement text to determine if a field is relevant and provide reasoning"""
    if req_id == "STANDARD":
        return "Standard meta field required for all entities in Informatica MDM"
    
    req_text_lower = req_text.lower()
    field_name_lower = field_name.lower()
    field_desc_lower = field_description.lower()
    
    reasoning_parts = []
    
    # Special analysis for FR-10 (do this first for more specific reasoning)
    if req_id == "FR-10":
        if 'constituentId' in field_name_lower or ('id' in field_name_lower and 'constituent' in field_name_lower):
            if 'unique' in req_text_lower or 'identifier' in req_text_lower:
                reasoning_parts.append("FR-10 explicitly mentions 'unique identifier' multiple times: 'Unique identifier are returned back to slate from banner', 'unique id generated/loaded back into slate', and 'MDM generated unique id (u1)'. This field is critical for cross-referencing between Slate, Banner, and MDM systems as described in the proposed flow.")
        elif 'firstname' in field_name_lower or 'lastname' in field_name_lower or 'first_name' in field_name_lower or 'last_name' in field_name_lower:
            if any(word in req_text_lower for word in ['student', 'prospect', 'constituent', 'application', 'customer']):
                reasoning_parts.append("FR-10 describes loading 'Student application information' from Slate and managing 'prospect' and 'constituent' data. Person identification fields (firstName, lastName) are essential for: (1) Loading prospect/student data from Slate into MDM, (2) Supporting reporting needs (e.g., '# of registration vs acceptance'), and (3) Creating master records that can be cross-referenced across systems.")
        elif 'state' in field_name_lower:
            if 'state' in req_text_lower or 'reporting by state' in req_text_lower:
                reasoning_parts.append("FR-10 explicitly mentions reporting examples including 'by state' (e.g., '# of registration vs acceptance by time, state, race'), requiring state information for demographic reporting.")
    
    # Check for direct mentions
    if field_name_lower in req_text_lower or any(word in req_text_lower for word in field_name_lower.split()):
        reasoning_parts.append(f"Field name '{field_name}' is mentioned or referenced in the requirement")
    
    # Check for semantic matches (only if no special reasoning found)
    if not reasoning_parts:
        semantic_keywords = {
            'firstName': ['name', 'first name', 'individual', 'person', 'student', 'prospect', 'constituent', 'customer', 'applicant'],
            'lastName': ['name', 'last name', 'surname', 'individual', 'person', 'student', 'prospect', 'constituent', 'customer', 'applicant'],
            'constituentId': ['unique id', 'unique identifier', 'identifier', 'id', 'constituent id', 'cross reference', 'join', 'relationship'],
            'state': ['state', 'location', 'geographic', 'reporting by state', 'demographic'],
            'dateOfBirth': ['birth', 'date of birth', 'dob', 'age', 'demographic', 'reporting by time'],
            'address': ['address', 'location', 'mailing', 'postal'],
            'phone': ['phone', 'telephone', 'contact'],
            'email': ['email', 'electronic address', 'contact'],
            'classification': ['classification', 'type', 'category', 'class'],
            'role': ['role', 'primary role', 'constituent role']
        }
        
        for keyword_group, keywords in semantic_keywords.items():
            if keyword_group in field_name_lower or any(kw in field_desc_lower for kw in keywords):
                matching_keywords = [kw for kw in keywords if kw in req_text_lower]
                if matching_keywords:
                    reasoning_parts.append(f"Requirement mentions concepts related to '{field_name}': {', '.join(matching_keywords[:3])}")
                    break
    
    # If no specific reasoning found, provide generic explanation
    if not reasoning_parts:
        if 'data integration' in req_text_lower or 'load' in req_text_lower or 'integration' in req_text_lower:
            reasoning_parts.append(f"Field '{field_name}' is a core person attribute needed for data integration and master data management")
        else:
            reasoning_parts.append(f"Field '{field_name}' supports the requirement's data model needs")
    
    return " | ".join(reasoning_parts) if reasoning_parts else f"Field '{field_name}' is relevant to requirement {req_id}"

def generate_data_model_from_brd(brd_file_path):
    """Generate data model JSON from BRD file"""
    
    # Parse BRD
    print("📄 Parsing BRD file...")
    with open(brd_file_path, 'rb') as f:
        brd_text = parse_document(f)
    
    print(f"✅ Parsed: {len(brd_text):,} characters")
    
    # Extract requirements
    print("📝 Analyzing requirements...")
    requirements = extract_requirements(brd_file_path)
    print(f"✅ Found {len(requirements)} requirements")
    
    # Show sample requirement
    if 'FR-10' in requirements:
        print(f"   Sample FR-10: {requirements['FR-10'][:100]}...")
    
    # Build prompts to understand context
    system_prompt, user_prompt = build_prompt(brd_text[:50000])  # Use first 50k chars for context
    
    # Based on BRD analysis, generate data model
    # Main entity: Person (Constituent)
    # Key requirements mention: addresses, phones, emails, roles, classifications, source systems
    
    data_model = {
        "entities": [
            {
                "name": "Person",
                "type": "BusinessEntity",
                "description": "Constituent master record for USF - represents students, alumni, staff, faculty, and other constituents",
                "fields": [
                    # OOTB Person fields
                    {
                        "name": "firstName",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Individual's first name",
                        "requirementIds": ["FR-1", "FR-10"],
                        "sourceRequirements": [build_source_requirement_text("FR-1", requirements), build_source_requirement_text("FR-10", requirements)]
                    },
                    {
                        "name": "lastName",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Individual's last name",
                        "requirementIds": ["FR-1", "FR-10"],
                        "sourceRequirements": [build_source_requirement_text("FR-1", requirements), build_source_requirement_text("FR-10", requirements)]
                    },
                    {
                        "name": "fullName",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Complete full name",
                        "requirementIds": ["FR-1"],
                        "sourceRequirements": [build_source_requirement_text("FR-1", requirements)]
                    },
                    {
                        "name": "dateOfBirth",
                        "dataType": "DateField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Date of birth",
                        "requirementIds": ["FR-1"],
                        "sourceRequirements": [build_source_requirement_text("FR-1", requirements)]
                    },
                    {
                        "name": "ssn",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Social Security Number",
                        "requirementIds": ["FR-1"],
                        "sourceRequirements": [build_source_requirement_text("FR-1", requirements)]
                    },
                    # Field Groups - PostalAddress
                    {
                        "name": "addressLine1",
                        "dataType": "TextField",
                        "fieldGroup": "PostalAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Street address line 1",
                        "requirementIds": ["FR-3", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-3", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "addressLine2",
                        "dataType": "TextField",
                        "fieldGroup": "PostalAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Street address line 2",
                        "requirementIds": ["FR-3", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-3", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "city",
                        "dataType": "TextField",
                        "fieldGroup": "PostalAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "City",
                        "requirementIds": ["FR-3", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-3", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "state",
                        "dataType": "TextField",
                        "fieldGroup": "PostalAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "State or province",
                        "requirementIds": ["FR-3", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-3", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "postalCode",
                        "dataType": "TextField",
                        "fieldGroup": "PostalAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Postal/ZIP code",
                        "requirementIds": ["FR-3", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-3", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "country",
                        "dataType": "TextField",
                        "fieldGroup": "PostalAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Country",
                        "requirementIds": ["FR-3", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-3", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "addressType",
                        "dataType": "LookupField",
                        "fieldGroup": "PostalAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": True,
                        "lookupEntity": "AddressType",
                        "description": "Type of address (billing, shipping, home, etc.)",
                        "requirementIds": ["FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    # Field Groups - Phone
                    {
                        "name": "phoneNumber",
                        "dataType": "TextField",
                        "fieldGroup": "Phone",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Phone number",
                        "requirementIds": ["FR-4", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-4", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "phoneType",
                        "dataType": "LookupField",
                        "fieldGroup": "Phone",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": True,
                        "lookupEntity": "PhoneType",
                        "description": "Type of phone (mobile, home, work, etc.)",
                        "requirementIds": ["FR-4", "FR-20", "FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-4", requirements), build_source_requirement_text("FR-20", requirements), build_source_requirement_text("FR-21", requirements)]
                    },
                    {
                        "name": "phoneCountryCode",
                        "dataType": "TextField",
                        "fieldGroup": "Phone",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Country code for phone number",
                        "requirementIds": ["FR-4"],
                        "sourceRequirements": [build_source_requirement_text("FR-4", requirements)]
                    },
                    # Field Groups - ElectronicAddress
                    {
                        "name": "electronicAddress",
                        "dataType": "TextField",
                        "fieldGroup": "ElectronicAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Email address",
                        "requirementIds": ["FR-1", "FR-21"],
                        "sourceRequirements": ["FR-1: Data Integration requirements", "FR-21: Data Model"]
                    },
                    {
                        "name": "electronicAddressType",
                        "dataType": "LookupField",
                        "fieldGroup": "ElectronicAddress",
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": True,
                        "lookupEntity": "ElectronicAddressType",
                        "description": "Type of electronic address (personal, work, etc.)",
                        "requirementIds": ["FR-21"],
                        "sourceRequirements": [build_source_requirement_text("FR-21", requirements)]
                    },
                    # Custom fields for USF
                    {
                        "name": "constituentId",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": True,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "USF constituent identifier",
                        "requirementIds": ["FR-1", "FR-10"],
                        "sourceRequirements": [build_source_requirement_text("FR-1", requirements), build_source_requirement_text("FR-10", requirements)]
                    },
                    {
                        "name": "classification",
                        "dataType": "LookupField",
                        "fieldGroup": None,
                        "isCustom": True,
                        "isRequired": False,
                        "isLookup": True,
                        "lookupEntity": "Classification",
                        "description": "Constituent classification (Full time staff, Part time staff, Student, Alumni, etc.)",
                        "requirementIds": ["FR-34"],
                        "sourceRequirements": [build_source_requirement_text("FR-34", requirements)]
                    },
                    {
                        "name": "primaryRole",
                        "dataType": "LookupField",
                        "fieldGroup": None,
                        "isCustom": True,
                        "isRequired": False,
                        "isLookup": True,
                        "lookupEntity": "ConstituentRole",
                        "description": "Primary role of the constituent (Student, Staff, Faculty, Alumni, etc.)",
                        "requirementIds": ["FR-22", "FR-23"],
                        "sourceRequirements": [build_source_requirement_text("FR-22", requirements), build_source_requirement_text("FR-23", requirements)]
                    },
                    # Meta fields
                    {
                        "name": "meta_businessId",
                        "dataType": "TextField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Unique business identifier",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements)]
                    },
                    {
                        "name": "meta_sourceSystem",
                        "dataType": "TextField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Source system name (Banner, Workday, Slate, ServiceNow, etc.)",
                        "requirementIds": ["STANDARD", "FR-6", "FR-7", "FR-8"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements), build_source_requirement_text("FR-6", requirements), build_source_requirement_text("FR-7", requirements), build_source_requirement_text("FR-8", requirements)]
                    },
                    {
                        "name": "meta_sourceSystemId",
                        "dataType": "TextField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "ID in the source system",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements)]
                    },
                    {
                        "name": "meta_activeFlag",
                        "dataType": "BooleanField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Active/inactive indicator",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements)]
                    },
                    {
                        "name": "meta_createdDate",
                        "dataType": "DateTimeField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Record creation timestamp",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements)]
                    },
                    {
                        "name": "meta_lastUpdateDate",
                        "dataType": "DateTimeField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Last update timestamp",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements)]
                    },
                    {
                        "name": "meta_createdBy",
                        "dataType": "TextField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "User who created the record",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements)]
                    },
                    {
                        "name": "meta_lastUpdatedBy",
                        "dataType": "TextField",
                        "fieldGroup": "_meta",
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "User who last updated the record",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": [build_source_requirement_text("STANDARD", requirements)]
                    }
                ]
            },
            # Reference Entities for LookupFields
            {
                "name": "AddressType",
                "type": "ReferenceEntity",
                "description": "Lookup values for address types",
                "fields": [
                    {
                        "name": "code",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Address type code",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "description",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Address type description",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "displayOrder",
                        "dataType": "IntegerField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Display order for UI",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "activeFlag",
                        "dataType": "BooleanField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Active/inactive indicator",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    }
                ]
            },
            {
                "name": "PhoneType",
                "type": "ReferenceEntity",
                "description": "Lookup values for phone types",
                "fields": [
                    {
                        "name": "code",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Phone type code",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "description",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Phone type description",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "displayOrder",
                        "dataType": "IntegerField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Display order for UI",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "activeFlag",
                        "dataType": "BooleanField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Active/inactive indicator",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    }
                ]
            },
            {
                "name": "ElectronicAddressType",
                "type": "ReferenceEntity",
                "description": "Lookup values for electronic address types",
                "fields": [
                    {
                        "name": "code",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Electronic address type code",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "description",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Electronic address type description",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "displayOrder",
                        "dataType": "IntegerField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Display order for UI",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "activeFlag",
                        "dataType": "BooleanField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Active/inactive indicator",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    }
                ]
            },
            {
                "name": "Classification",
                "type": "ReferenceEntity",
                "description": "Lookup values for constituent classifications",
                "fields": [
                    {
                        "name": "code",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Classification code",
                        "requirementIds": ["STANDARD", "FR-34"],
                        "sourceRequirements": ["Standard reference entity field", "FR-34: Classification field for ServiceNow integration"]
                    },
                    {
                        "name": "description",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Classification description",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "displayOrder",
                        "dataType": "IntegerField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Display order for UI",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "activeFlag",
                        "dataType": "BooleanField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Active/inactive indicator",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    }
                ]
            },
            {
                "name": "ConstituentRole",
                "type": "ReferenceEntity",
                "description": "Lookup values for constituent roles",
                "fields": [
                    {
                        "name": "code",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": True,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Role code",
                        "requirementIds": ["STANDARD", "FR-22", "FR-23"],
                        "sourceRequirements": ["Standard reference entity field", "FR-22: Primary role for survivorship", "FR-23: Primary role for survivorship"]
                    },
                    {
                        "name": "description",
                        "dataType": "TextField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Role description",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "displayOrder",
                        "dataType": "IntegerField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Display order for UI",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    },
                    {
                        "name": "activeFlag",
                        "dataType": "BooleanField",
                        "fieldGroup": None,
                        "isCustom": False,
                        "isRequired": False,
                        "isLookup": False,
                        "lookupEntity": None,
                        "description": "Active/inactive indicator",
                        "requirementIds": ["STANDARD"],
                        "sourceRequirements": ["Standard reference entity field"]
                    }
                ]
            }
        ],
        "relationships": [
            {
                "fromEntity": "Person",
                "toEntity": "AddressType",
                "relationshipType": "hasMany",
                "description": "Person can have multiple addresses with different types"
            },
            {
                "fromEntity": "Person",
                "toEntity": "PhoneType",
                "relationshipType": "hasMany",
                "description": "Person can have multiple phone numbers with different types"
            },
            {
                "fromEntity": "Person",
                "toEntity": "ElectronicAddressType",
                "relationshipType": "hasMany",
                "description": "Person can have multiple email addresses with different types"
            },
            {
                "fromEntity": "Person",
                "toEntity": "Classification",
                "relationshipType": "hasOne",
                "description": "Person has one classification"
            },
            {
                "fromEntity": "Person",
                "toEntity": "ConstituentRole",
                "relationshipType": "hasOne",
                "description": "Person has one primary role"
            }
        ]
    }
    
    # Add reasoning to all fields
    print("📝 Adding field reasoning for all requirements...")
    for entity in data_model.get("entities", []):
        for field in entity.get("fields", []):
            requirement_ids = field.get("requirementIds", [])
            if requirement_ids:
                field_name = field.get("name", "")
                field_description = field.get("description", "")
                field["fieldReasoning"] = build_field_reasoning(field_name, field_description, requirement_ids, requirements)
    
    return data_model

if __name__ == "__main__":
    import sys
    
    brd_file = sys.argv[1] if len(sys.argv) > 1 else "USF Requirements Document - Phase 0B.xlsx"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "generated_data_model.json"
    
    print("=" * 80)
    print("GENERATING DATA MODEL FROM BRD (Using Cursor AI)")
    print("=" * 80)
    
    try:
        data_model = generate_data_model_from_brd(brd_file)
        
        # Save JSON
        print(f"\n✅ Saving data model to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(data_model, f, indent=2)
        
        # Statistics
        entities = data_model.get('entities', [])
        business_entities = [e for e in entities if e.get('type') == 'BusinessEntity']
        total_fields = sum(len(e.get('fields', [])) for e in business_entities)
        
        print(f"✅ Data model generated successfully!")
        print(f"   Business Entities: {len(business_entities)}")
        print(f"   Reference Entities: {len(entities) - len(business_entities)}")
        print(f"   Total Fields: {total_fields}")
        print(f"   Relationships: {len(data_model.get('relationships', []))}")
        print(f"\n✅ Saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

