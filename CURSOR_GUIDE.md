# Cursor AI Guide - Modular Pipeline Usage

This guide explains how Cursor can use the modular pipeline functions for iterative refinement.

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
**What it does:** Creates Cursor AI prompt from BRD text  
**Returns:** Path to prompt file, or `None` if error

---

### Step 3: Cursor AI Processing
**Manual step** - Cursor needs to:
1. Read the prompt file
2. Generate JSON data model
3. Save JSON to outputs folder

**Cursor command:**
```
Read outputs/[filename]_prompt.txt and generate the data model JSON following all instructions. Save it to outputs/[filename]_response.json
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
```python
# Cursor should:
# 1. Read the prompt file
# 2. Generate JSON following the prompt instructions
# 3. Save to outputs/[filename]_response.json
```

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
├── [filename]_response.json      # Step 3 output (Cursor generates)
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

