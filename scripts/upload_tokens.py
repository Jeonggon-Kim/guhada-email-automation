import sys
import os
# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration
TABLE_NAME = 'EmailBot_Tokens'
TOKEN_FILE = 'tokens.json'

def upload_tokens():
    """Upload local tokens.json to DynamoDB"""
    
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: {TOKEN_FILE} not found. Please login locally first.")
        return

    try:
        # Read local tokens
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
        
        print("Read local tokens successfully.")
        
        # Prepare item for DynamoDB
        item = {
            'token_id': 'default',
            'access_token': tokens.get('access_token'),
            'refresh_token': tokens.get('refresh_token'),
            'expires_in': tokens.get('expires_in'),
            'id_token': tokens.get('id_token'),
            'scope': tokens.get('scope')
        }
        
        # Remove None values
        item = {k: v for k, v in item.items() if v is not None}
        
        # Connect to DynamoDB (Defaulting to Seoul region)
        dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
        table = dynamodb.Table(TABLE_NAME)
        
        # Upload
        table.put_item(Item=item)
        print(f"✓ Successfully uploaded tokens to DynamoDB table '{TABLE_NAME}'")
        
    except Exception as e:
        print(f"Error uploading tokens: {str(e)}")
        print("\nMake sure you have:")
        print("1. Created the DynamoDB table 'EmailBot_Tokens' (Partition key: token_id (String))")
        print("2. Configured AWS credentials (aws configure)")

if __name__ == '__main__':
    upload_tokens()
