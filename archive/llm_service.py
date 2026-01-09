"""
LLM Service - Generic Interface for Multiple LLM Providers
Supports Groq, Claude, and other LLM APIs
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMService(ABC):
    """Abstract base class for LLM services"""
    
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response from LLM
        
        Args:
            system_prompt: System prompt/instructions
            user_prompt: User prompt/content
            temperature: Temperature for generation (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
        
        Returns:
            dict with:
                - 'content' (str): Generated text
                - 'usage' (dict): Token usage info with 'input_tokens', 'output_tokens', 'total_tokens'
                - 'model' (str): Model used
                - 'stop_reason' (str): Why generation stopped (optional)
        """
        pass
    
    def generate_data_model(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate data model from BRD using LLM
        
        Args:
            system_prompt: System prompt with instructions
            user_prompt: User prompt with BRD content
        
        Returns:
            dict with:
                - 'data_model' (dict): Parsed JSON data model
                - 'raw_response' (str): Raw response from LLM
                - 'usage' (dict): Token usage info
                - 'model' (str): Model used
                - 'stop_reason' (str): Why generation stopped (optional)
        """
        try:
            # Call LLM API
            response = self.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.0  # Deterministic for data model generation
            )
            
            content = response["content"].strip()
            
            # Extract and parse JSON from response
            json_content = self._extract_json(content)
            
            # Parse JSON
            try:
                data_model = json.loads(json_content)
            except json.JSONDecodeError as e:
                raise Exception(
                    f"Failed to parse JSON from LLM response: {str(e)}\n"
                    f"Response content (first 500 chars): {content[:500]}"
                )
            
            return {
                "data_model": data_model,
                "raw_response": content,
                "usage": response["usage"],
                "model": response["model"],
                "stop_reason": response.get("stop_reason", "unknown")
            }
            
        except Exception as e:
            raise Exception(f"Error generating data model: {str(e)}")
    
    @staticmethod
    def _extract_json(content: str) -> str:
        """
        Extract JSON from LLM response
        Handles cases where JSON is wrapped in markdown code blocks
        
        Args:
            content: Raw content from LLM
        
        Returns:
            Extracted JSON string
        """
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            # Find the closing ```
            end_index = content.find("```", 7)
            if end_index != -1:
                content = content[7:end_index].strip()
        elif content.startswith("```"):
            # Generic code block
            end_index = content.find("```", 3)
            if end_index != -1:
                content = content[3:end_index].strip()
        
        return content


class GroqService(LLMService):
    """Service for interacting with Groq API (fast LLM inference)"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, max_tokens: Optional[int] = None):
        """
        Initialize Groq service
        
        Args:
            api_key: Groq API key. If not provided, reads from KEY env var (or GROQ_API_KEY as fallback)
            model: Groq model to use. If not provided, reads from GROQ_MODEL env var or uses default
            max_tokens: Maximum tokens. If not provided, reads from GROQ_MAX_TOKENS env var or uses default
        """
        try:
            from groq import Groq
        except ImportError:
            raise ImportError(
                "groq package not installed. "
                "Install it with: pip install groq"
            )
        
        # Check for API key - prioritize KEY, then GROQ_API_KEY
        self.api_key = api_key or os.getenv("KEY") or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. "
                "Set KEY or GROQ_API_KEY environment variable or pass api_key parameter"
            )
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.max_tokens = max_tokens or int(os.getenv("GROQ_MAX_TOKENS", "4096"))
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Groq
        
        Args:
            system_prompt: System prompt/instructions
            user_prompt: User prompt/content
            temperature: Temperature for generation (0.0 = deterministic)
            max_tokens: Maximum tokens to generate (defaults to instance max_tokens)
        
        Returns:
            dict with 'content' (str), 'usage' (dict), and 'model' (str)
        """
        try:
            max_tokens = max_tokens or self.max_tokens
            
            # Groq API uses messages format similar to OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Make API call using Groq SDK
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                stream=False  # We want complete response, not streaming
            )
            
            # Extract content
            content = completion.choices[0].message.content if completion.choices else ""
            
            # Extract usage information
            usage_data = completion.usage if hasattr(completion, 'usage') else {}
            
            return {
                "content": content,
                "usage": {
                    "input_tokens": getattr(usage_data, 'prompt_tokens', 0) if hasattr(usage_data, 'prompt_tokens') else usage_data.get("prompt_tokens", 0),
                    "output_tokens": getattr(usage_data, 'completion_tokens', 0) if hasattr(usage_data, 'completion_tokens') else usage_data.get("completion_tokens", 0),
                    "total_tokens": getattr(usage_data, 'total_tokens', 0) if hasattr(usage_data, 'total_tokens') else usage_data.get("total_tokens", 0)
                },
                "model": completion.model if hasattr(completion, 'model') else self.model,
                "stop_reason": completion.choices[0].finish_reason if completion.choices else "stop"
            }
            
        except Exception as e:
            raise Exception(f"Error calling Groq API: {str(e)}")


class ClaudeService(LLMService):
    """Service for interacting with Anthropic's Claude API"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, max_tokens: Optional[int] = None):
        """
        Initialize Claude service
        
        Args:
            api_key: Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var
            model: Claude model to use. If not provided, reads from CLAUDE_MODEL env var or uses default
            max_tokens: Maximum tokens. If not provided, reads from CLAUDE_MAX_TOKENS env var or uses default
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install it with: pip install anthropic"
            )
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter"
            )
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = max_tokens or int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Claude
        
        Args:
            system_prompt: System prompt/instructions
            user_prompt: User prompt/content
            temperature: Temperature for generation (0.0 = deterministic)
            max_tokens: Maximum tokens to generate (defaults to instance max_tokens)
        
        Returns:
            dict with 'content' (str), 'usage' (dict), and 'model' (str)
        """
        try:
            max_tokens = max_tokens or self.max_tokens
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            # Extract content from message
            content = ""
            if message.content:
                # Content is a list of content blocks
                for block in message.content:
                    if block.type == "text":
                        content += block.text
            
            return {
                "content": content,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens
                },
                "model": message.model,
                "stop_reason": getattr(message, "stop_reason", "stop")
            }
            
        except Exception as e:
            raise Exception(f"Error calling Claude API: {str(e)}")


def get_llm_service(provider: str = "groq", **kwargs) -> LLMService:
    """
    Factory function to get an LLM service instance
    
    Args:
        provider: LLM provider name ("groq", "claude", etc.). Default: "groq"
        **kwargs: Additional arguments to pass to service constructor
    
    Returns:
        LLMService instance
    
    Examples:
        >>> service = get_llm_service("groq")  # Default
        >>> service = get_llm_service("claude")
        >>> service = get_llm_service("groq", model="llama-3.1-70b-versatile", max_tokens=8192)
        >>> service = get_llm_service("groq", api_key="your-key-here")
    """
    provider = provider.lower()
    
    if provider == "groq" or provider == "grok":  # Support both spellings
        return GroqService(**kwargs)
    elif provider == "claude":
        return ClaudeService(**kwargs)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported providers: 'groq', 'claude'"
        )
