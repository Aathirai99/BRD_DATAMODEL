# BRD Data Model Core - Complete Project Flow

## 📋 Project Overview
Converts Business Requirements Documents (BRD) Excel files into Informatica MDM data models using Cursor AI analysis (no external LLM API calls).

---

## 🏗️ Project Structure

```
brd-datamodel-core/
├── 📄 Core Modules
│   ├── parsers.py                    # Excel parsing utilities
│   └── prompts.py                    # Prompt templates & builders
│
├── 🎯 Data Model Generation
│   └── generate_data_model_manual.py  # Cursor-based data model generation
│
├── 📊 Reporting
│   └── generate_data_model_report.py  # HTML report generator
│
├── 🚀 Orchestration
│   ├── run_full_pipeline.py          # Complete pipeline runner
│   └── app.py                        # Main entry point
│
├── 📁 archive/                       # Archived LLM API files
│   ├── llm_service.py
│   └── generators.py
│
└── 📁 tests/                         # Test files
    └── [various test files]
```

---

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: BRD Excel File                        │
│              (e.g., "USF Requirements Document Cleaned.xlsx")  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │   STEP 1: Parse Excel File         │
        │   File: parsers.py                 │
        │   Function: parse_document()      │
        │                                    │
        │   • Reads all Excel sheets         │
        │   • Extracts all cell text         │
        │   • Returns: BRD text (string)      │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   STEP 2: Extract Requirements    │
        │   File: generate_data_model_       │
        │         manual.py                  │
        │   Function: extract_requirements() │
        │                                    │
        │   • Reads Excel structure          │
        │   • Finds "Functional Requirements"│
        │   • Extracts FR-XX, DQR-XX IDs     │
        │   • Gets full requirement text      │
        │   • Returns: dict {FR-1: text, ...}│
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   STEP 3: Build Context            │
        │   File: generate_data_model_       │
        │         manual.py                  │
        │   Uses: prompts.py                 │
        │                                    │
        │   • Calls build_prompt()           │
        │   • Gets system prompt template    │
        │   • Creates user prompt with BRD   │
        │   • (For context, not API call)    │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   STEP 4: Generate Data Model      │
        │   File: generate_data_model_       │
        │         manual.py                  │
        │   Function: generate_data_model_   │
        │              from_brd()            │
        │                                    │
        │   • Analyzes BRD requirements      │
        │   • Creates entity definitions      │
        │   • Maps fields to requirements    │
        │   • Generates field reasoning      │
        │   • Creates relationships          │
        │   • Returns: data_model (dict)     │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   STEP 5: Add Field Reasoning     │
        │   File: generate_data_model_       │
        │         manual.py                  │
        │   Function: build_field_reasoning()│
        │                                    │
        │   • For each field & requirement    │
        │   • Analyzes requirement text      │
        │   • Generates justification        │
        │   • Adds to fieldReasoning dict    │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   OUTPUT: JSON Data Model          │
        │   File: generated_data_model.json  │
        │                                    │
        │   Structure:                       │
        │   {                                │
        │     "entities": [...],             │
        │     "relationships": [...]         │
        │   }                                │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   STEP 6: Analyze Data Model      │
        │   File: generate_data_model_       │
        │         report.py                  │
        │   Function: analyze_entity()       │
        │                                    │
        │   • Categorizes fields             │
        │   • Groups by field groups         │
        │   • Maps requirements to fields    │
        │   • Calculates statistics          │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   STEP 7: Generate HTML Report    │
        │   File: generate_data_model_       │
        │         report.py                  │
        │   Function: generate_html_report() │
        │                                    │
        │   • Creates HTML with CSS          │
        │   • Shows entity details           │
        │   • Displays field reasoning       │
        │   • Shows relationships            │
        │   • Includes traceability          │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────┐
        │   OUTPUT: HTML Report              │
        │   File: data_model_report.html     │
        │                                    │
        │   • Interactive HTML report        │
        │   • Dark grey-blue theme           │
        │   • Full requirement text           │
        │   • Field reasoning visible         │
        └────────────────────────────────────┘
```

---

## 📝 Detailed Function Flow

### Entry Points

#### 1. **app.py** (Main Entry Point)
```python
app.py
  └──> run_full_pipeline()
```

#### 2. **run_full_pipeline.py** (Pipeline Runner)
```python
run_full_pipeline()
  ├──> Check file exists
  ├──> generate_data_model_from_brd()  [from generate_data_model_manual.py]
  │     ├──> parse_document()          [from parsers.py]
  │     ├──> extract_requirements()    [from generate_data_model_manual.py]
  │     ├──> build_prompt()            [from prompts.py]
  │     ├──> Create data model structure
  │     └──> build_field_reasoning()   [from generate_data_model_manual.py]
  ├──> Save JSON
  └──> generate_html_report()          [from generate_data_model_report.py]
        ├──> load_data_model()
        ├──> analyze_entity()
        └──> Generate HTML
```

#### 3. **generate_data_model_manual.py** (Standalone)
```python
if __name__ == "__main__":
  └──> generate_data_model_from_brd()
        └──> [same flow as above]
```

---

## 🔧 Key Functions & Their Roles

### **parsers.py**
- `parse_document(file) -> str`
  - Input: Excel file object
  - Output: All text from all sheets
  - Purpose: Extract raw BRD content

- `get_document_stats(text) -> Dict`
  - Input: Text string
  - Output: {characters, words, pages}
  - Purpose: Get BRD statistics

### **prompts.py**
- `build_prompt(brd_text, platform) -> (system_prompt, user_prompt)`
  - Input: BRD text, platform type
  - Output: System and user prompts
  - Purpose: Build context for data model generation
  - Note: Used for context, not for API calls

### **generate_data_model_manual.py**

#### Core Functions:
1. **`extract_requirements(brd_file_path) -> dict`**
   - Reads Excel directly
   - Finds Functional Requirements sheet
   - Extracts FR-XX, DQR-XX with full text
   - Returns: `{FR-1: "full text", FR-2: "full text", ...}`

2. **`build_source_requirement_text(req_id, requirements_dict) -> str`**
   - Formats requirement text
   - Returns: `"FR-10: Full requirement description..."`

3. **`analyze_requirement_for_fields(req_id, req_text, field_name, field_desc) -> str`**
   - Analyzes why a field was chosen
   - Looks for keywords and semantic matches
   - Special handling for specific requirements (e.g., FR-10)
   - Returns: Reasoning text

4. **`build_field_reasoning(field_name, field_desc, requirement_ids, requirements_dict) -> dict`**
   - Builds reasoning for all requirements mapped to a field
   - Returns: `{FR-1: "reasoning", FR-10: "reasoning", ...}`

5. **`generate_data_model_from_brd(brd_file_path) -> dict`**
   - Main generation function
   - Orchestrates the entire process
   - Returns: Complete data model JSON structure

### **generate_data_model_report.py**

#### Core Functions:
1. **`load_data_model(json_file) -> dict`**
   - Loads JSON data model
   - Returns: Data model dictionary

2. **`analyze_entity(entity) -> dict`**
   - Categorizes fields (identifiers, attributes, field groups, meta)
   - Maps requirements to fields
   - Extracts requirement text
   - Returns: Analysis dictionary

3. **`generate_html_report(data_model, output_file) -> str`**
   - Generates comprehensive HTML report
   - Includes all entities, fields, relationships
   - Shows requirement traceability with reasoning
   - Returns: Output file path

---

## 📊 Data Model Structure

### Input: BRD Excel File
```
Excel File
├── Sheet: "Functional Requirements"
│   ├── Column: FR #
│   ├── Column: Functional Requirements Description
│   └── Column: Comments
└── Sheet: "BPs and Steps"
    └── [Business processes]
```

### Output: JSON Data Model
```json
{
  "entities": [
    {
      "name": "Person",
      "type": "BusinessEntity",
      "description": "...",
      "fields": [
        {
          "name": "firstName",
          "dataType": "TextField",
          "fieldGroup": null,
          "isCustom": false,
          "isRequired": true,
          "isLookup": false,
          "lookupEntity": null,
          "description": "Individual's first name",
          "requirementIds": ["FR-1", "FR-10"],
          "sourceRequirements": ["FR-1: ...", "FR-10: ..."],
          "fieldReasoning": {
            "FR-1": "Reasoning text...",
            "FR-10": "Reasoning text..."
          }
        }
      ]
    }
  ],
  "relationships": [
    {
      "fromEntity": "Person",
      "toEntity": "AddressType",
      "relationshipType": "hasMany",
      "description": "..."
    }
  ]
}
```

### Output: HTML Report
- Executive Summary (statistics)
- Entity Analysis (detailed field breakdown)
- Requirement Traceability (with full text & reasoning)
- Entity Relationships
- Field Groups Summary

---

## 🚀 Usage Examples

### Option 1: Complete Pipeline
```bash
python app.py "USF Requirements Document Cleaned.xlsx"
```

### Option 2: Pipeline Script
```bash
python run_full_pipeline.py "USF Requirements Document Cleaned.xlsx"
```

### Option 3: Generate Data Model Only
```bash
python generate_data_model_manual.py "USF Requirements Document Cleaned.xlsx" generated_data_model.json
```

### Option 4: Generate Report Only
```bash
python generate_data_model_report.py generated_data_model.json data_model_report.html
```

---

## 🔗 File Dependencies

```
app.py
  └──> run_full_pipeline.py

run_full_pipeline.py
  ├──> generate_data_model_manual.py
  │     ├──> parsers.py
  │     └──> prompts.py
  └──> generate_data_model_report.py

generate_data_model_manual.py
  ├──> parsers.py
  └──> prompts.py

generate_data_model_report.py
  └──> (standalone, reads JSON)
```

---

## 🎯 Key Features

1. **No External API Calls**: Uses Cursor AI for analysis, no LLM API needed
2. **Full Requirement Extraction**: Reads Excel structure to get complete requirement text
3. **Field Reasoning**: Explains why each field was chosen for each requirement
4. **Comprehensive Reporting**: HTML report with full traceability
5. **Requirement Mapping**: Maps fields to specific requirements (FR-XX, DQR-XX)
6. **Entity Relationships**: Defines relationships between entities
7. **Field Groups**: Supports Informatica MDM field groups (PostalAddress, Phone, etc.)

---

## 📦 Output Files

1. **generated_data_model.json**
   - Complete data model structure
   - All entities, fields, relationships
   - Requirement mappings with reasoning

2. **data_model_report.html**
   - Interactive HTML report
   - Dark grey-blue theme
   - Full requirement text
   - Field reasoning visible
   - Entity relationships diagram

---

## 🔄 Processing Steps Summary

1. **Parse** → Extract text from Excel
2. **Extract** → Get requirements from Excel structure
3. **Analyze** → Understand BRD content (using prompts for context)
4. **Generate** → Create data model structure
5. **Reason** → Add field selection reasoning
6. **Report** → Generate HTML visualization

---

## ✨ Key Advantages

- ✅ No API rate limits or costs
- ✅ Fast processing (no network calls)
- ✅ Full control over generation logic
- ✅ Complete requirement traceability
- ✅ Detailed field reasoning
- ✅ Professional HTML reports

