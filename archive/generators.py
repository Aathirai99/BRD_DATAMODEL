"""
Data Model Generator
Orchestrates parsing, prompting, and LLM generation to create data models from BRDs
"""

from typing import Dict, Any, Optional
from parsers import parse_document, get_document_stats
from prompts import build_prompt
from llm_service import get_llm_service, LLMService


def generate_data_model_from_file(
    file_path: str,
    provider: str = "groq",
    api_key: Optional[str] = None,
    platform: str = "informatica",
    llm_service: Optional[LLMService] = None,
    **llm_kwargs
) -> Dict[str, Any]:
    """
    Generate data model from BRD Excel file
    
    Args:
        file_path: Path to Excel BRD file
        provider: LLM provider name ("groq", "claude", etc.). Default: "groq"
        api_key: Optional API key (if not provided, uses env var for the provider)
        platform: Platform type (default: "informatica")
        llm_service: Optional pre-initialized LLM service. If provided, provider/api_key are ignored
        **llm_kwargs: Additional arguments to pass to LLM service constructor (model, max_tokens, etc.)
    
    Returns:
        dict containing:
            - data_model: Parsed JSON data model
            - raw_response: Raw JSON string from LLM
            - usage: Token usage information
            - model: Model used
            - stop_reason: Why generation stopped
            - brd_stats: Statistics about parsed BRD
    
    Examples:
        >>> # Use Groq (default)
        >>> result = generate_data_model_from_file("brd.xlsx")
        
        >>> # Use specific model
        >>> result = generate_data_model_from_file("brd.xlsx", model="llama-3.1-70b-versatile")
    """
    try:
        # Step 1: Parse the BRD file
        with open(file_path, 'rb') as f:
            brd_text = parse_document(f)
        
        # Step 2: Build prompts
        system_prompt, user_prompt = build_prompt(brd_text, platform=platform)
        
        # Step 3: Initialize or use provided LLM service
        if llm_service is None:
            if api_key:
                llm_kwargs['api_key'] = api_key
            llm_service = get_llm_service(provider=provider, **llm_kwargs)
        
        # Step 4: Generate data model
        result = llm_service.generate_data_model(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Step 5: Add BRD statistics
        brd_stats = get_document_stats(brd_text)
        
        result["brd_stats"] = brd_stats
        result["brd_length"] = len(brd_text)
        result["file_path"] = file_path
        result["provider"] = provider if not hasattr(llm_service, '__class__') else llm_service.__class__.__name__
        
        return result
        
    except Exception as e:
        raise Exception(f"Error generating data model from file: {str(e)}")


def generate_data_model_from_text(
    brd_text: str,
    provider: str = "groq",
    api_key: Optional[str] = None,
    platform: str = "informatica",
    llm_service: Optional[LLMService] = None,
    **llm_kwargs
) -> Dict[str, Any]:
    """
    Generate data model from BRD text (already parsed)
    
    Args:
        brd_text: BRD text content
        provider: LLM provider name ("groq", "claude", etc.). Default: "groq"
        api_key: Optional API key (if not provided, uses env var for the provider)
        platform: Platform type (default: "informatica")
        llm_service: Optional pre-initialized LLM service. If provided, provider/api_key are ignored
        **llm_kwargs: Additional arguments to pass to LLM service constructor (model, max_tokens, etc.)
    
    Returns:
        dict containing data model and metadata
    
    Examples:
        >>> # Use Groq (default)
        >>> result = generate_data_model_from_text(brd_text)
        
        >>> # Use specific model
        >>> result = generate_data_model_from_text(brd_text, model="llama-3.1-70b-versatile")
    """
    try:
        # Step 1: Build prompts
        system_prompt, user_prompt = build_prompt(brd_text, platform=platform)
        
        # Step 2: Initialize or use provided LLM service
        if llm_service is None:
            if api_key:
                llm_kwargs['api_key'] = api_key
            llm_service = get_llm_service(provider=provider, **llm_kwargs)
        
        # Step 3: Generate data model
        result = llm_service.generate_data_model(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Step 4: Add BRD statistics
        brd_stats = get_document_stats(brd_text)
        
        result["brd_stats"] = brd_stats
        result["brd_length"] = len(brd_text)
        result["provider"] = provider if not hasattr(llm_service, '__class__') else llm_service.__class__.__name__
        
        return result
        
    except Exception as e:
        raise Exception(f"Error generating data model from text: {str(e)}")
