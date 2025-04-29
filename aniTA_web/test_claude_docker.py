import os
import json
import django
from django.conf import settings
from anthropic import Anthropic

# Initialize Django to access settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

def test_claude_api():
    try:
        # Get API key from settings
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))
        if not api_key:
            print("ERROR: No API key found in settings or environment variables")
            return False
            
        print(f"API key found: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
        
        # Initialize client
        client = Anthropic(api_key=api_key)
        model = "claude-3-haiku-20240307"
        
        # Simple test prompt that should return structured data
        prompt = """
        Please provide a grading report for a test submission.
        Format your response as a JSON with the following structure:
        {
          "total_score": 85,
          "results": [
            {
              "question": "Question 1",
              "score": 85,
              "justification": "This is good work because..."
            }
          ]
        }
        """
        
        print(f"Calling Claude API with model: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            system="You are a helpful AI assistant for academic grading. Please respond with a JSON object containing grade information.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        print(f"Response received, length: {len(content)}")
        print(f"Response preview: {content[:200]}...")
        
        # Try to parse as JSON
        import re
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            print("Found JSON in code block format")
            json_str = json_match.group(1)
        else:
            print("Searching for raw JSON in response")
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print("Found raw JSON object")
            else:
                print("No JSON found, using raw content")
                json_str = content
        
        print(f"Extracted JSON string (first 200 chars): {json_str[:200]}...")
        
        try:
            result = json.loads(json_str)
            print(f"Parsed JSON successfully")
            print(f"Keys: {result.keys()}")
            print(f"Total score: {result.get('total_score')}")
            print(f"Results count: {len(result.get('results', []))}")
            return True
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
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