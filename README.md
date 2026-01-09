# BRD Datamodel Core

A Python project for processing and generating data models from Business Requirements Documents (BRD).

## Project Structure

- `app.py` - Main application entry point
- `parsers.py` - Document parsing utilities
- `prompts.py` - LLM prompt templates
- `llm_service.py` - LLM service integration
- `generators.py` - Data model generation logic

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key to `.env`

3. Run the application:
```bash
python app.py
```

## Testing

Run the test script to verify API key configuration:
```bash
python test.py
```

