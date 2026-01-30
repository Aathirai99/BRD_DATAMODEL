# Cursor AI Guide - Modular Pipeline Usage

This guide explains how Cursor can use the modular pipeline functions for iterative refinement.

---

## Pipeline Flow (What Actually Runs)

1. **Step 1: Parse**  
   Excel FRD → `parsers.parse_document()` → **brd_text** (raw FRD).

2. **Step 2: Build final prompt**  
   - **parse output** (brd_text)  
   - **prompts.py** output: `INFORMATICA_SYSTEM_PROMPT` + `build_enhanced_prompt()`  
   - **OOTB reference**: `load_person_fields_catalog()` reads **ootb_person_reference.txt**  
   → Combined into **one final prompt** and saved as `outputs/[filename]_prompt.txt`.

3. **Step 3: Give prompt to AI → execute → JSON**  
   - **Input**: the file `outputs/[filename]_prompt.txt` (parse + prompts.py + OOTB).  
   - **Action**: **AI reads that file**, follows the instructions, **produces the data model JSON**.  
   - **Output**: JSON saved to `outputs/[filename]_response.json`.  
   - **This only happens when the AI (Cursor) actually receives and executes that prompt.**  
   Running `run_full_pipeline` does *not* run the AI; it only builds the prompt and prints instructions.

4. **Step 4: Visualizations**  
   JSON → Draw.io + HTML.

**Check:** Is the AI really getting the prompt and producing the JSON? Only if you explicitly **read** `*_prompt.txt` and **output** the JSON (e.g. “Read `outputs/X_prompt.txt` and generate the data model JSON; save to `outputs/X_response.json`”). Otherwise Step 3 is skipped and any JSON comes from elsewhere (e.g. a script).

---

## Modular Step Functions

The pipeline is broken into **4 independent steps** that can be called separately:

### Step 1: Parse BRD
```python
from run_full_pipeline import step1_parse_brd

# Auto-detect Excel file
brd_text, outputs = step1_parse_brd()

# Or specify file
brd_text, outputs = step1_parse_brd("path/to/brd.xlsx")
```
**What it does:** Finds Excel file, parses it, extracts all text  
**Returns:** `(brd_text, outputs_dict)` or `(None, None)` if error

---

### Step 2: Generate Prompt
```python
from run_full_pipeline import step2_generate_prompt

prompt_path = step2_generate_prompt(brd_text, outputs)
```
**What it does:** Builds the **final prompt** = **parse output (FRD)** + **prompts.py** (system + user template) + **ootb_person_reference.txt**; saves to `outputs/[filename]_prompt.txt`.  
**Returns:** Path to prompt file, or `None` if error

---

### Step 3: Give prompt to AI → execute → JSON
**Input:** `outputs/[filename]_prompt.txt` (already contains **parse output + prompts.py + OOTB reference**).

**You must:** Give that prompt to the AI (Cursor). The AI reads it, executes it, and outputs **only** the data model JSON. Save that output to `outputs/[filename]_response.json`.

**What the prompt tells the AI to do:**
- Analyze the FRD (and use the OOTB catalog) to produce an Informatica MDM data model
- **CRITICAL:** Scan ALL FRD requirements for explicit field names (e.g., "CWID", "PIDM", "Classification")
- Check if explicitly mentioned fields exist in OOTB catalog
- Include BOTH OOTB fields AND explicit custom fields (isCustom: true) in the data model
- Return JSON with `metadata`, `reasoning` (entityDecisions, fieldDecisions), `dataModel` (entities, relationships)
- Apply OOTB-first, traceability (requirementIds/sourceRequirements), no _meta fields
- Output **only** raw JSON (no markdown, no code, no preamble)

**Do not** use a Python script to build the JSON. The JSON must come from the **AI executing the prompt**.

**Optional Pre-check:** Before generating JSON, you can run the custom field analyzer:
```python
python analyze_custom_fields.py "USF Requirements Document Cleaned.xlsx"
```
This helps identify explicit custom fields that must be included.

**Cursor command (so the AI actually receives and runs the prompt):**
```
Read outputs/[filename]_prompt.txt and generate the data model JSON following all instructions. 
Ensure you scan the FRD for explicit custom fields (CWID, PIDM, Classification, source system IDs, etc.) 
and include them with isCustom: true. Save it to outputs/[filename]_response.json
```

---

### Step 4: Generate Visualizations
```python
from run_full_pipeline import step4_generate_visualizations

# Auto-detect JSON
drawio, html = step4_generate_visualizations()

# Or specify JSON
drawio, html = step4_generate_visualizations("outputs/response.json")
```
**What it does:** Creates Draw.io diagram and HTML report from JSON  
**Returns:** `(drawio_path, html_path)` or `(None, None)` if error

---

## Complete Workflow Examples

### Example 1: Full Pipeline (First Time)
```python
from run_full_pipeline import run_full_pipeline

# Runs all steps automatically
run_full_pipeline()
```

### Example 2: Regenerate Just Visualizations
```python
from run_full_pipeline import step4_generate_visualizations

# User says: "I don't like the visualizations, regenerate them"
drawio, html = step4_generate_visualizations()
```

### Example 3: Regenerate Prompt (After BRD Changes)
```python
from run_full_pipeline import step1_parse_brd, step2_generate_prompt

# User says: "The BRD changed, regenerate the prompt"
brd_text, outputs = step1_parse_brd()
step2_generate_prompt(brd_text, outputs)
```

### Example 4: Regenerate Everything After JSON Update
```python
from run_full_pipeline import step4_generate_visualizations

# User says: "I updated the JSON, regenerate visualizations"
step4_generate_visualizations()
```

---

## Cursor AI Commands

### When User Says: "Process the Excel file"
```python
from run_full_pipeline import run_full_pipeline
run_full_pipeline()
```

### When User Says: "I don't like this iteration, do it again"
**If they mean visualizations:**
```python
from run_full_pipeline import step4_generate_visualizations
step4_generate_visualizations()
```

**If they mean prompt:**
```python
from run_full_pipeline import step1_parse_brd, step2_generate_prompt
brd_text, outputs = step1_parse_brd()
step2_generate_prompt(brd_text, outputs)
```

**If they mean everything:**
```python
from run_full_pipeline import run_full_pipeline
run_full_pipeline()
```

### When User Says: "Generate the data model from the prompt"
The **AI** (Cursor) should:
1. Read the prompt file (catalog + FRD + rules)
2. **Analyze** the FRD and **generate** the JSON (no script — AI output only)
3. Save the AI’s JSON to `outputs/[filename]_response.json`

### When User Says: "Create the visualizations"
```python
from run_full_pipeline import step4_generate_visualizations
step4_generate_visualizations()
```

---

## File Structure

```
outputs/
├── [filename]_prompt.txt          # Step 2 output
├── [filename]_response.json      # Step 3 output (AI generates from prompt — not a script)
├── [filename]_data_model.drawio   # Step 4 output
└── [filename]_data_model_report.html  # Step 4 output
```

---

## Key Points for Cursor

1. **Each step is independent** - Can be called separately
2. **Steps return useful data** - Can pass outputs between steps
3. **Auto-detection** - Functions can find files automatically
4. **Error handling** - Functions return None on error
5. **Iterative refinement** - User can regenerate any step independently
6. **Step 3 = AI output only** - The JSON must be generated by the AI from the prompt. Do not use a Python script to build it.

---

## Regenerate Function

For convenience, there's a `regenerate_step()` function:

```python
from run_full_pipeline import regenerate_step

# Regenerate specific step
regenerate_step('parse')
regenerate_step('prompt')
regenerate_step('visualizations')
```

