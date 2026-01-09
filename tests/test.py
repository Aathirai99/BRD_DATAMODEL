"""
Test script to verify Anthropic API key loads correctly.
"""
import os
from dotenv import load_dotenv

def test_api_key():
    """Test if the Anthropic API key is loaded correctly."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if api_key:
        if api_key.strip():  # Check if it's not just whitespace
            print("✓ API key loaded successfully!")
            print(f"✓ API key length: {len(api_key)} characters")
            print(f"✓ API key starts with: {api_key[:10]}...")
            return True
        else:
            print("✗ API key is empty (only whitespace)")
            return False
    else:
        print("✗ API key not found in environment variables")
        print("  Please set ANTHROPIC_API_KEY in your .env file")
        return False

if __name__ == "__main__":
    print("Testing Anthropic API key configuration...")
    print("-" * 50)
    success = test_api_key()
    print("-" * 50)
    if success:
        print("Test passed!")
    else:
        print("Test failed! Please check your .env file.")

