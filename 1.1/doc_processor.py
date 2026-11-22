import boto3
import json
from prompt_template import PromptTemplateManager

# Initialize clients
s3 = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime', 'us-east-1')

def process_document(bucket, key, model_id='us.anthropic.claude-opus-4-7'):
    # Get document from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    document_text = response['Body'].read().decode('utf-8')
    ptm = PromptTemplateManager()
    
    # Invoke Bedrock model
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 5000,
            "messages": [
                {"role": "user", "content": ptm.get_prompt('extract_info', document_text=document_text)}
            ]
        })
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    extracted_info = response_body['content'][0]['text']
    
    summary_response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": ptm.get_prompt('generate_summary', extracted_info=extracted_info)}
            ]
        })
    )
    
    summary_body = json.loads(summary_response['body'].read())
    summary = summary_body['content'][0]['text']
    
    return {
        "extracted_info": extracted_info,
        "summary": summary
    }

# Example usage
# if __name__ == "__main__":
#     result = process_document('claim-documents-poc-xyz', 'claims/claim1.txt')
#     print(json.dumps(result, indent=2))
