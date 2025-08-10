import os
import json
import requests
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class LLMHandler:
    def __init__(self):
        """Initialize both AWS Bedrock and Gemini LLM handlers."""
        
        # AWS Bedrock setup (Primary)
        self.bedrock_region = os.getenv("BEDROCK_REGION", "us-east-1")
        self.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
        self.bedrock_available = False
        self.bedrock_client = None
        
        try:
            self.bedrock_client = boto3.client("bedrock-runtime", region_name=self.bedrock_region)
            # Test connection with a simple call
            self._test_bedrock_connection()
            self.bedrock_available = True
            print(f"✅ AWS Bedrock initialized - Model: {self.bedrock_model_id}")
        except Exception as e:
            print(f"⚠️  AWS Bedrock unavailable: {e}")
            self.bedrock_available = False
        
        # Gemini setup (Fallback)
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_url_env = os.getenv('GEMINI_URL')
        self.gemini_available = False
        self.gemini_url = None
        
        if self.gemini_api_key and self.gemini_url_env:
            self.gemini_url = f"{self.gemini_url_env}={self.gemini_api_key}"
            self.gemini_available = True
            print(f"✅ Gemini initialized as fallback")
        else:
            print(f"⚠️  Gemini fallback unavailable - Missing API key or URL")
        
        # Validate at least one LLM is available
        if not self.bedrock_available and not self.gemini_available:
            raise ValueError("Neither AWS Bedrock nor Gemini API are available. Please check your configuration.")
    
    def _test_bedrock_connection(self):
        """Test Bedrock connection with a minimal request."""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
            }
            payload = json.dumps(body).encode("utf-8")
            self.bedrock_client.invoke_model(
                modelId=self.bedrock_model_id,
                body=payload,
                accept="application/json",
                contentType="application/json",
            )
        except Exception as e:
            raise Exception(f"Bedrock connection test failed: {e}")
    
    def invoke_primary_llm(self, prompt, max_tokens=40000, temperature=0.1):
        """
        Invoke the primary LLM (AWS Bedrock Claude).
        
        Args:
            prompt (str): The prompt to send to the LLM
            max_tokens (int): Maximum tokens in response
            temperature (float): Temperature for response generation
            
        Returns:
            dict: {
                'success': bool,
                'response': str or None,
                'model': str,
                'agent': str,
                'error': str or None
            }
        """
        if not self.bedrock_available:
            return {
                'success': False,
                'response': None,
                'model': 'None',
                'agent': 'AWS Bedrock (Unavailable)',
                'error': 'AWS Bedrock not available'
            }
        
        try:
            print("🔄 Analyzing with AWS Claude Haiku...")
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            }
            
            payload = json.dumps(body).encode("utf-8")
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model_id,
                body=payload,
                accept="application/json",
                contentType="application/json",
            )
            
            result = json.loads(response["body"].read().decode("utf-8"))
            response_text = result["content"][0]["text"]
            
            return {
                'success': True,
                'response': response_text,
                'model': self.bedrock_model_id,
                'agent': 'AWS Claude Haiku',
                'error': None
            }
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            error_msg = f"Bedrock ClientError ({error_code}): {e}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'response': None,
                'model': self.bedrock_model_id,
                'agent': 'AWS Claude Haiku',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Bedrock unexpected error: {e}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'response': None,
                'model': self.bedrock_model_id,
                'agent': 'AWS Claude Haiku',
                'error': error_msg
            }
    
    def invoke_secondary_llm(self, prompt, max_tokens=1000, temperature=0.1):
        """
        Invoke the secondary LLM (Gemini).
        
        Args:
            prompt (str): The prompt to send to the LLM
            max_tokens (int): Maximum tokens in response
            temperature (float): Temperature for response generation
            
        Returns:
            dict: Same format as invoke_primary_llm
        """
        if not self.gemini_available:
            return {
                'success': False,
                'response': None,
                'model': 'None',
                'agent': 'Gemini (Unavailable)',
                'error': 'Gemini not available'
            }
        
        try:
            print("🔄 Falling back to Gemini...")
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": max_tokens
                }
            }

            response = requests.post(self.gemini_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    response_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    return {
                        'success': True,
                        'response': response_text,
                        'model': 'gemini-pro',
                        'agent': 'Gemini (Fallback)',
                        'error': None
                    }
                else:
                    error_msg = "Gemini returned empty candidates"
                    return {
                        'success': False,
                        'response': None,
                        'model': 'gemini-pro',
                        'agent': 'Gemini (Fallback)',
                        'error': error_msg
                    }
            else:
                error_msg = f"Gemini HTTP error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                
                return {
                    'success': False,
                    'response': None,
                    'model': 'gemini-pro',
                    'agent': 'Gemini (Fallback)',
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Gemini request timeout"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'response': None,
                'model': 'gemini-pro',
                'agent': 'Gemini (Fallback)',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Gemini unexpected error: {e}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'response': None,
                'model': 'gemini-pro',
                'agent': 'Gemini (Fallback)',
                'error': error_msg
            }
    
    def invoke_with_fallback(self, prompt, max_tokens=1000, temperature=0.1):
        """
        Invoke LLM with automatic fallback from primary to secondary.
        
        Args:
            prompt (str): The prompt to send to the LLM
            max_tokens (int): Maximum tokens in response
            temperature (float): Temperature for response generation
            
        Returns:
            dict: Same format as individual invoke methods
        """
        # Try primary LLM first
        result = self.invoke_primary_llm(prompt, max_tokens, temperature)
        
        if result['success']:
            print(f"✅ Analysis completed using {result['agent']}")
            return result
        
        # Fallback to secondary LLM
        print(f"⚠️  Primary LLM failed: {result['error']}")
        result = self.invoke_secondary_llm(prompt, max_tokens, temperature)
        
        if result['success']:
            print(f"✅ Analysis completed using {result['agent']}")
            return result
        
        # Both failed
        print("❌ Both AI agents failed")
        return {
            'success': False,
            'response': None,
            'model': 'None',
            'agent': 'None (All Failed)',
            'error': 'Both primary and secondary LLMs failed'
        }
    
    def get_status(self):
        """Get status of both LLM services."""
        return {
            'primary': {
                'name': 'AWS Bedrock Claude',
                'model': self.bedrock_model_id,
                'available': self.bedrock_available
            },
            'secondary': {
                'name': 'Gemini',
                'model': 'gemini-pro',
                'available': self.gemini_available
            }
        }
    
    def get_available_models(self):
        """Get list of available models."""
        models = []
        if self.bedrock_available:
            models.append({
                'name': self.bedrock_model_id,
                'provider': 'AWS Bedrock',
                'type': 'primary'
            })
        if self.gemini_available:
            models.append({
                'name': 'gemini-pro',
                'provider': 'Google',
                'type': 'secondary'
            })
        return models


# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize the LLM handler
        llm = LLMHandler()
        
        # Show status
        print("\n" + "="*50)
        print("LLM Handler Status:")
        status = llm.get_status()
        for key, info in status.items():
            status_icon = "✅" if info['available'] else "❌"
            print(f"  {key.title()}: {status_icon} {info['name']} ({info['model']})")
        
        # Test with a simple prompt
        print("\n" + "="*50)
        print("Testing LLM with sample prompt...")
        
        test_prompt = "Explain what a missing HTML title tag means in one sentence."
        result = llm.invoke_with_fallback(test_prompt, max_tokens=100)
        
        if result['success']:
            print(f"\n✅ Test successful!")
            print(f"Model: {result['model']}")
            print(f"Agent: {result['agent']}")
            print(f"Response: {result['response']}")
        else:
            print(f"\n❌ Test failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ LLM Handler initialization failed: {e}")