"""
Quick test to verify Groq API connection
"""
import os
import sys
# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from llm_service import GroqService, get_llm_service

load_dotenv()

def test_grok_connection():
    """Test if Groq API is working"""
    print("=" * 80)
    print("TESTING GROQ API CONNECTION")
    print("=" * 80)
    
    try:
        # Check for API key
        key = os.getenv('KEY') or os.getenv('GROQ_API_KEY')
        if not key:
            print("\n❌ API key not found!")
            print("   Please set KEY or GROQ_API_KEY in your .env file")
            return False
        
        print(f"\n✅ API key found: {key[:10]}... (length: {len(key)})")
        
        # Initialize service
        print("\n✅ Initializing Groq service...")
        service = get_llm_service("groq")
        print(f"   Model: {service.model}")
        print(f"   Max tokens: {service.max_tokens:,}")
        
        # Test with a simple question
        print("\n✅ Testing API connection with a simple question...")
        print("   Question: 'What is 2+2? Answer in one sentence.'")
        
        system_prompt = "You are a helpful assistant."
        user_prompt = "What is 2+2? Answer in one sentence."
        
        response = service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
            max_tokens=50
        )
        
        print("\n✅ API connection successful!")
        print(f"   Response: {response['content']}")
        print(f"   Model: {response['model']}")
        print(f"   Usage:")
        print(f"      Input tokens: {response['usage']['input_tokens']}")
        print(f"      Output tokens: {response['usage']['output_tokens']}")
        print(f"      Total tokens: {response['usage']['total_tokens']}")
        print(f"   Stop reason: {response.get('stop_reason', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("✅ GROQ API CONNECTION TEST PASSED!")
        print("=" * 80)
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ API Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_grok_connection()
    exit(0 if success else 1)

