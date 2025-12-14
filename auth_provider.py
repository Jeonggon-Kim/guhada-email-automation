import json
import os
from msal import ConfidentialClientApplication
import config

class AuthProvider:
    """Handles Microsoft authentication and token management"""
    
    def __init__(self):
        self.app = ConfidentialClientApplication(
            config.CLIENT_ID,
            authority=config.AUTHORITY,
            client_credential=config.CLIENT_SECRET,
        )
        self.token_cache = None
    
    def get_auth_url(self):
        """Generate authorization URL for user login"""
        auth_url = self.app.get_authorization_request_url(
            scopes=config.SCOPES,
            redirect_uri=config.REDIRECT_URI
        )
        return auth_url
    
    def acquire_token_by_code(self, code):
        """Exchange authorization code for access token"""
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=config.SCOPES,
            redirect_uri=config.REDIRECT_URI
        )
        
        if 'error' in result:
            raise Exception(f"Authentication error: {result.get('error_description')}")
        
        # Save tokens
        self.save_tokens(result)
        return result
    
    def get_access_token(self):
        """Get valid access token (refresh if needed)"""
        tokens = self.load_tokens()
        
        if not tokens:
            raise Exception('No tokens found. Please authenticate first.')
        
        # Try to get token silently using refresh token
        result = self.app.acquire_token_by_refresh_token(
            refresh_token=tokens.get('refresh_token'),
            scopes=config.SCOPES
        )
        
        if 'error' in result:
            raise Exception(f"Token refresh error: {result.get('error_description')}")
        
        # Save updated tokens
        self.save_tokens(result)
        return result['access_token']
    
    def save_tokens(self, token_response):
        """Save tokens to file"""
        tokens = {
            'access_token': token_response.get('access_token'),
            'refresh_token': token_response.get('refresh_token'),
            'expires_in': token_response.get('expires_in'),
            'id_token': token_response.get('id_token'),
        }
        
        with open(config.TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        self.token_cache = tokens
    
    def load_tokens(self):
        """Load tokens from file"""
        if self.token_cache:
            return self.token_cache
        
        if not os.path.exists(config.TOKEN_FILE):
            return None
        
        try:
            with open(config.TOKEN_FILE, 'r') as f:
                self.token_cache = json.load(f)
            return self.token_cache
        except Exception as e:
            print(f"Error loading tokens: {e}")
            return None
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        tokens = self.load_tokens()
        return tokens is not None and 'refresh_token' in tokens

# Singleton instance
auth_provider = AuthProvider()
