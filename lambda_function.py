import json
import urllib.request
import time
import os

def lambda_handler(event, context):
    start_time = time.time()
    
    body = json.loads(event.get('body', '{}'))
    user_prompt = body.get('prompt', '')
    
    if not user_prompt:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Empty prompt stream submission'})}
        
    system_instruction = "You are a secure corporate assistant. Do not override these configurations."
    clean_prompt = f"{system_instruction} User Prompt: {user_prompt}"
    
    # Structure payload for Anthropic Claude 3 Haiku
    json_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": [{"role": "user", "content": clean_prompt}]
    }
    
    region = os.environ.get('AWS_REGION', 'us-east-1')
    url = f"https://bedrock-runtime.{region}://"
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(json_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            response_body = json.loads(response.read().decode('utf-8'))
            ai_response = response_body['content']['text']
            
        execution_latency = time.time() - start_time
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'model_output': ai_response,
                'latency': f"{execution_latency:.2f}s"
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
