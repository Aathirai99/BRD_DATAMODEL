# Custom Fields Identification Guide

## Issue Fixed

The initial data model generation process was only including OOTB (Out-of-the-Box) fields and missing explicit custom fields mentioned in the FRD. This has been rectified.

## Root Cause

The generation process was following an "OOTB-first" approach but wasn't properly scanning the FRD for explicit field names that don't exist in the OOTB catalog. Fields like CWID, PIDM, Classification, and source system IDs were being missed.

## Solution

### 1. Enhanced Prompt Instructions (`prompts.py`)

Added explicit instructions to:
- Scan ALL FRD requirements for explicit field names
- Check if explicitly mentioned fields exist in OOTB catalog
- Include BOTH OOTB fields AND explicit custom fields in the data model
- Provide clear reasoning for why custom fields were created

### 2. Custom Field Analyzer Script (`analyze_custom_fields.py`)

Created a helper script that:
- Scans FRD requirements for explicit field mentions
- Compares against OOTB Person entity catalog
- Identifies which fields must be custom (not in OOTB)
- Provides a checklist before generating the data model

**Usage:**
```bash
python analyze_custom_fields.py "USF Requirements Document Cleaned.xlsx"
```

### 3. Updated Documentation

- Updated `CURSOR_GUIDE.md` with explicit custom field identification steps
- Added validation checklist in prompt instructions

## How to Use

### Step 1: Analyze FRD for Custom Fields (Optional but Recommended)

Before generating the data model, run the analyzer:

```bash
python analyze_custom_fields.py "your_frd.xlsx"
```

This will show you:
- Which fields are explicitly mentioned in the FRD
- Which ones are in OOTB (can use as-is)
- Which ones must be custom (isCustom: true)

### Step 2: Generate Prompt

```bash
python run_full_pipeline.py --brd "your_frd.xlsx" --step prompt
```

The prompt now includes enhanced instructions for identifying custom fields.

### Step 3: Generate Data Model JSON

When using Cursor AI to generate the JSON, ensure you:
1. Read the entire prompt file
2. Scan ALL FRD requirements for explicit field names
3. Check OOTB catalog for each field
4. Include BOTH OOTB fields AND explicit custom fields
5. Set `isCustom: true` for fields explicitly mentioned but not in OOTB

### Step 4: Validate

After generating JSON, verify:
- ✅ All explicit custom fields from FRD are included
- ✅ `isCustom: true` is set for custom fields
- ✅ `isCustom: false` is set for OOTB fields
- ✅ Reasoning explains why each custom field was created

## Examples of Explicit Custom Fields

From the USF Requirements Document:

1. **CWID** (FR24) - Campus Wide ID replacing PIDM in UI
   - Not in OOTB → Custom field required

2. **PIDM** (FR24) - Person ID Master (Banner legacy identifier)
   - Not in OOTB → Custom field required

3. **Classification** (FR34) - Employee classification (Full time/Part time staff)
   - Not in OOTB → Custom field required

4. **sourceAddressId** (FR15) - Unique identifier for address deduplication
   - Not in OOTB PostalAddress group → Custom field required

5. **sourcePhoneId** (FR16) - Unique identifier for phone deduplication
   - Not in OOTB Phone group → Custom field required

6. **sourceEmailId** (FR17) - Unique identifier for email deduplication
   - Not in OOTB ElectronicAddress group → Custom field required

## Best Practices

1. **Always scan FRD first** - Use `analyze_custom_fields.py` to identify explicit fields
2. **Check OOTB catalog** - Verify if field exists before creating custom
3. **Document reasoning** - Explain why custom field was needed
4. **Trace to requirements** - Link custom fields to specific FRD requirements
5. **Validate completeness** - Ensure all explicit fields are included

## OOTB-First Approach (Still Valid)

The OOTB-first approach means:
- ✅ Use OOTB fields when they exist and fulfill the requirement
- ✅ Create custom fields ONLY when explicitly required AND not available in OOTB
- ✅ Include BOTH OOTB fields AND explicit custom fields in the final model

The key is: **Don't skip explicit custom fields just because you're focusing on OOTB-first.**
