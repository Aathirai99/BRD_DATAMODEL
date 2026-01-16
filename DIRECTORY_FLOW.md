# Directory Flow & Pipeline Architecture

## 📁 Directory Structure

```
brd-datamodel-core/
│
├── 📄 INPUT FILES (Root Directory)
│   └── USF Requirements Document Cleaned.xlsx  [Input: BRD Excel file]
│
├── 🐍 CORE MODULES
│   ├── run_full_pipeline.py          [Orchestrator: Main entry point]
│   ├── parsers.py                     [Module: Excel parsing logic]
│   ├── prompts.py                     [Module: Prompt template generation]
│   ├── cursor_workflow.py             [Module: Cursor AI integration helpers]
│   ├── generators.py                  [Module: Visualization generation]
│   └── visual_config.py               [Module: Visual styling configuration]
│
├── 📋 DOCUMENTATION
│   ├── README.md                      [User guide & quick start]
│   ├── CURSOR_GUIDE.md                [Cursor AI workflow guide]
│   └── DIRECTORY_FLOW.md              [This file - architecture overview]
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt               [Python dependencies]
│   └── .gitignore                     [Git ignore rules]
│
└── 📤 OUTPUTS DIRECTORY
    └── outputs/
        ├── [filename]_prompt.txt                    [Step 2 Output]
        ├── [filename]_response.json                 [Step 3 Output]
        ├── [filename]_data_model.drawio            [Step 4 Output]
        └── [filename]_data_model_report.html       [Step 4 Output]
```

---

## 🔄 Complete Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STEP 1: PARSE BRD                            │
│                                                                     │
│  Input:  USF Requirements Document Cleaned.xlsx                    │
│  Module: parsers.py → parse_document()                             │
│  Process: Read Excel → Extract all sheets → Convert to text        │
│  Output: brd_text (string)                                         │
│                                                                     │
│  Function: step1_parse_brd() in run_full_pipeline.py              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP 2: GENERATE PROMPT                          │
│                                                                     │
│  Input:  brd_text (from Step 1)                                    │
│  Module: cursor_workflow.py → save_prompt_to_file()                │
│           prompts.py → INFORMATICA_SYSTEM_PROMPT                   │
│  Process: Combine system prompt + BRD text → Format for Cursor     │
│  Output: [filename]_prompt.txt                                     │
│                                                                     │
│  Function: step2_generate_prompt() in run_full_pipeline.py        │
│  Location: outputs/[filename]_prompt.txt                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 3: CURSOR AI PROCESSING (Manual)                  │
│                                                                     │
│  Input:  outputs/[filename]_prompt.txt                             │
│  Process: Manual - Read prompt → Generate JSON data model          │
│  Output: [filename]_response.json                                  │
│                                                                     │
│  Function: Manual step (Cursor AI generates JSON)                  │
│  Location: outputs/[filename]_response.json                        │
│                                                                     │
│  JSON Structure:                                                    │
│  {                                                                  │
│    "metadata": {...},                                               │
│    "reasoning": {...},                                              │
│    "dataModel": {                                                   │
│      "entities": [...],                                             │
│      "relationships": [...]                                         │
│    }                                                                │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 4: GENERATE VISUALIZATIONS                        │
│                                                                     │
│  Input:  outputs/[filename]_response.json                          │
│  Module: cursor_workflow.py → parse_cursor_response()              │
│           generators.py → save_drawio_file()                        │
│           generators.py → generate_html_report()                    │
│           visual_config.py → Styling & configuration                │
│                                                                     │
│  Process:                                                           │
│    1. Parse & validate JSON                                        │
│    2. Generate Draw.io XML diagram                                 │
│    3. Generate HTML report with traceability                       │
│                                                                     │
│  Output:                                                            │
│    - [filename]_data_model.drawio                                  │
│    - [filename]_data_model_report.html                             │
│                                                                     │
│  Function: step4_generate_visualizations() in run_full_pipeline.py│
│  Location: outputs/[filename]_data_model.*                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Module Dependencies & Relationships

```
run_full_pipeline.py (Orchestrator)
    │
    ├──► parsers.py
    │    └──► parse_document()       [Excel → Text]
    │
    ├──► cursor_workflow.py
    │    ├──► save_prompt_to_file()  [Text → Prompt file]
    │    └──► parse_cursor_response() [JSON → Data model dict]
    │         │
    │         └──► prompts.py
    │              └──► INFORMATICA_SYSTEM_PROMPT [Template]
    │
    └──► generators.py
         ├──► save_drawio_file()     [Data model → Draw.io XML]
         └──► generate_html_report() [Data model → HTML report]
              │
              └──► visual_config.py
                   └──► Styling & color configuration
```

---

## 📊 File Naming Convention

All output files follow a consistent naming pattern based on the input Excel filename:

```
Input:  "USF Requirements Document Cleaned.xlsx"
        ↓
Base:   "usf_requirements_document_cleaned"
        ↓
Outputs:
  - usf_requirements_document_cleaned_prompt.txt
  - usf_requirements_document_cleaned_response.json
  - usf_requirements_document_cleaned_data_model.drawio
  - usf_requirements_document_cleaned_data_model_report.html
```

**Naming Rules:**
1. Convert to lowercase
2. Replace spaces with underscores
3. Replace hyphens with underscores
4. Append descriptive suffix for each file type

---

## 🎯 Function Call Flow

### Entry Point: `run_full_pipeline.py`

```python
# Main execution flow
run_full_pipeline()
    │
    ├── step1_parse_brd()
    │   └── parsers.parse_document() → returns brd_text
    │
    ├── step2_generate_prompt(brd_text, outputs)
    │   └── cursor_workflow.save_prompt_to_file()
    │       └── prompts.build_prompt()
    │           └── prompts.INFORMATICA_SYSTEM_PROMPT
    │
    ├── step3_cursor_instructions(outputs)  [Manual step - instructions only]
    │
    └── step4_generate_visualizations(json_path, outputs)
        ├── cursor_workflow.parse_cursor_response() → data_model
        ├── generators.save_drawio_file(data_model)
        └── generators.generate_html_report(data_model)
```

### Modular Step Functions (Can be called independently)

```python
# Step 1: Parse BRD
brd_text, outputs = step1_parse_brd(brd_file_path=None)

# Step 2: Generate Prompt
prompt_path = step2_generate_prompt(brd_text, outputs)

# Step 3: Manual (Cursor AI generates JSON)

# Step 4: Generate Visualizations
drawio_path, html_path = step4_generate_visualizations(json_path=None, outputs=None)
```

---

## 📦 Module Responsibilities

### 1. `run_full_pipeline.py` - Orchestrator
- **Role**: Main entry point, coordinates all steps
- **Functions**: 
  - `run_full_pipeline()` - Full pipeline execution
  - `step1_parse_brd()` - BRD parsing
  - `step2_generate_prompt()` - Prompt generation
  - `step4_generate_visualizations()` - Visualization generation
  - `regenerate_step()` - Selective step regeneration

### 2. `parsers.py` - Data Extraction
- **Role**: Parse Excel files into text
- **Functions**:
  - `parse_document()` - Extract all text from Excel sheets
  - `get_document_stats()` - Calculate statistics

### 3. `prompts.py` - Prompt Templates
- **Role**: Define AI prompt structure
- **Content**:
  - `INFORMATICA_SYSTEM_PROMPT` - System instructions for AI
  - `build_prompt()` - Combine system prompt + BRD text

### 4. `cursor_workflow.py` - Cursor AI Integration
- **Role**: Bridge between pipeline and Cursor AI
- **Functions**:
  - `generate_cursor_prompt()` - Format prompt for Cursor
  - `save_prompt_to_file()` - Save prompt to file
  - `parse_cursor_response()` - Load and validate JSON response
  - `validate_data_model()` - Validate JSON structure

### 5. `generators.py` - Visualization Generation
- **Role**: Create visual outputs from data model
- **Functions**:
  - `save_drawio_file()` - Generate Draw.io XML diagram
  - `generate_html_report()` - Generate HTML report with traceability

### 6. `visual_config.py` - Visual Configuration
- **Role**: Define colors, styles, and visual settings
- **Content**: Color schemes, entity type styling, diagram layout

---

## 🔄 Iterative Workflow Patterns

### Pattern 1: Full Pipeline (First Time)
```
Excel → Parse → Prompt → [Manual: JSON] → Visualizations
```

### Pattern 2: Regenerate Prompt Only
```
Excel → Parse → Prompt (regenerate)
```

### Pattern 3: Regenerate Visualizations Only
```
Existing JSON → Visualizations (regenerate)
```

### Pattern 4: Complete Regeneration
```
Excel → Parse → Prompt → [Manual: New JSON] → Visualizations
```

---

## 📂 Output Directory Structure

```
outputs/
│
├── [filename]_prompt.txt                    # Cursor AI prompt (Step 2)
│   └── Contains: System prompt + BRD text
│
├── [filename]_response.json                 # Data model JSON (Step 3)
│   └── Contains: {
│         "metadata": {...},
│         "reasoning": {...},
│         "dataModel": {
│           "entities": [...],
│           "relationships": [...]
│         }
│       }
│
├── [filename]_data_model.drawio            # Draw.io diagram (Step 4)
│   └── Contains: XML format for Draw.io
│   └── Opens in: https://app.diagrams.net
│
└── [filename]_data_model_report.html       # HTML report (Step 4)
    └── Contains: Interactive HTML with:
        - Entity documentation
        - Field details
        - Requirement traceability
        - Relationships visualization
        - Searchable interface
```

---

## 🚀 Usage Patterns

### 1. Command Line - Full Pipeline
```bash
python run_full_pipeline.py
```

### 2. Command Line - Specific BRD
```bash
python run_full_pipeline.py --brd "path/to/brd.xlsx"
```

### 3. Command Line - Visualizations Only
```bash
python run_full_pipeline.py --visuals-only
```

### 4. Python API - Modular Steps
```python
from run_full_pipeline import (
    step1_parse_brd,
    step2_generate_prompt,
    step4_generate_visualizations
)

# Step 1
brd_text, outputs = step1_parse_brd()

# Step 2
prompt_path = step2_generate_prompt(brd_text, outputs)

# Step 3: Manual (Cursor generates JSON)

# Step 4
drawio, html = step4_generate_visualizations()
```

### 5. Python API - Full Pipeline
```python
from run_full_pipeline import run_full_pipeline

run_full_pipeline()
```

---

## 🔍 Key Design Principles

1. **Modularity**: Each step is independent and can be run separately
2. **Auto-detection**: Functions can find files automatically if paths not provided
3. **Error Handling**: Functions return `None` on error for graceful failure
4. **Iterative Refinement**: Support for regenerating individual steps
5. **Traceability**: Requirement IDs and references preserved throughout pipeline
6. **Separation of Concerns**: Clear module boundaries and responsibilities

---

## 📝 Data Model Structure

The JSON response follows this structure:

```json
{
  "metadata": {
    "originalBRD": "...",
    "generatedDate": "YYYY-MM-DD",
    "platform": "informatica"
  },
  "reasoning": {
    "summary": "...",
    "entityDecisions": [...],
    "fieldDecisions": [...]
  },
  "dataModel": {
    "entities": [
      {
        "name": "EntityName",
        "type": "BusinessEntity|ReferenceEntity",
        "fields": [...]
      }
    ],
    "relationships": [...]
  }
}
```

---

## 🎨 Visualization Outputs

### Draw.io Diagram
- Entity-relationship diagram
- Visual representation of data model
- Color-coded by entity type
- Interactive editing in Draw.io

### HTML Report
- Comprehensive documentation
- Requirement traceability
- Searchable interface
- Field-level details
- Relationship mapping
- Responsive design

---

This architecture supports both automated workflows and iterative refinement cycles.

