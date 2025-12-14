import os
from dotenv import load_dotenv

load_dotenv()

# Microsoft Azure Configuration
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID', 'common')
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/auth/callback')

# Microsoft Graph API Scopes
# Microsoft Graph API Scopes
SCOPES = [
    'User.Read',
    'Mail.ReadWrite',
    'Mail.Send'
]

# Webhook Configuration
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 5000))

# LLM Configuration - Google Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# User Configuration
USER_EMAIL = os.getenv('USER_EMAIL')

# Token storage
TOKEN_FILE = 'tokens.json'
