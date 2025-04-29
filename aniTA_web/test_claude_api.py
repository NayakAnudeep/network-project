import os
import json
from anthropic import Anthropic
from django.conf import settings
import django

# Initialize Django to access settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

def test_claude_api():
    # Get API key from settings or environment variables
    try:
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))
        if not api_key:
            print("ERROR: No API key found in settings or environment variables")
            return False
            
        print(f"API key found: {api_key[:5]}...{api_key[-5:]}")
        
        # Initialize client
        client = Anthropic(api_key=api_key)
        model = "claude-3-haiku-20240307"
        
        # Simple test prompt
        prompt = "Please format your response as JSON with a field called total_score with a numeric value of 85, and a field called results that's an array with one object containing question: 'Test Question', score: 85, and justification: 'This is a test'."
        
        print(f"Calling Claude API with model: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            system="You are a helpful assistant. Always format your responses as JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        print(f"Response received, length: {len(content)}")
        print(f"Response preview: {content[:200]}...")
        
        # Try to parse as JSON
        try:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                print("Found JSON in code block format")
                json_str = json_match.group(1)
            else:
                print("Searching for raw JSON in response")
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                json_str = json_match.group(1) if json_match else content
                
            result = json.loads(json_str)
            print(f"Successfully parsed JSON: {result}")
            total_score = result.get('total_score')
            print(f"Total score: {total_score}")
            return True
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw content: {content}")
            return False
            
    except Exception as e:
        print(f"Error testing Claude API: {e}")
        return False

if __name__ == "__main__":
    print("Testing Claude API connection...")
    success = test_claude_api()
    if success:
        print("✅ API test successful")
    else:
        print("❌ API test failed")