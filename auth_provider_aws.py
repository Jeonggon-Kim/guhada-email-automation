import json
import os
import boto3
from msal import ConfidentialClientApplication
import config

class AWSAuthProvider:
    """Handles Microsoft authentication using DynamoDB for token storage"""
    
    def __init__(self):
        self.app = ConfidentialClientApplication(
            config.CLIENT_ID,
            authority=config.AUTHORITY,
            client_credential=config.CLIENT_SECRET,
        )
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('DYNAMODB_TABLE', 'EmailBot_Tokens')
        self.table = self.dynamodb.Table(self.table_name)
        self.token_cache = None
    
    def get_access_token(self):
        """Get valid access token (refresh if needed)"""
        tokens = self.load_tokens()
        
        if not tokens:
            raise Exception('No tokens found in DynamoDB. Please run local setup first to generate tokens.')
        
        # Try to get token silently using refresh token
        # This automatically handles token refresh if expired
        result = self.app.acquire_token_by_refresh_token(
            refresh_token=tokens.get('refresh_token'),
            scopes=config.SCOPES
        )
        
        if 'error' in result:
            raise Exception(f"Token refresh error: {result.get('error_description')}")
        
        # Save updated tokens if they changed
        if result.get('access_token') != tokens.get('access_token'):
            self.save_tokens(result)
            
        return result['access_token']
    
    def save_tokens(self, token_response):
        """Save tokens to DynamoDB"""
        tokens = {
            'token_id': 'default',  # Primary Key
            'access_token': token_response.get('access_token'),
            'refresh_token': token_response.get('refresh_token'),
            'expires_in': token_response.get('expires_in'),
            'id_token': token_response.get('id_token'),
            'scope': token_response.get('scope')
        }
        
        # Remove None values
        tokens = {k: v for k, v in tokens.items() if v is not None}
        
        self.table.put_item(Item=tokens)
        self.token_cache = tokens
        print("✓ Tokens updated in DynamoDB")
    
    def load_tokens(self):
        """Load tokens from DynamoDB"""
        if self.token_cache:
            return self.token_cache
            
        try:
            response = self.table.get_item(Key={'token_id': 'default'})
            if 'Item' in response:
                self.token_cache = response['Item']
                return self.token_cache
            return None
        except Exception as e:
            print(f"Error loading tokens from DynamoDB: {e}")
            return None

# Singleton instance
aws_auth_provider = AWSAuthProvider()
