import requests

class GraphClient:
    """Microsoft Graph API client for email operations"""
    
    BASE_URL = 'https://graph.microsoft.com/v1.0'
    
    def __init__(self):
        self.access_token = None
        self.auth_provider = None
    
    def _get_headers(self):
        """Get authorization headers"""
        # Lazy load auth provider if not injected
        if not self.auth_provider:
            try:
                from auth_provider import auth_provider
                self.auth_provider = auth_provider
            except ImportError:
                raise Exception("Auth provider not configured. Inject it or ensure auth_provider.py exists.")

        if not self.access_token:
            self.access_token = self.auth_provider.get_access_token()
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_message(self, message_id):
        """Get email message by ID"""
        url = f'{self.BASE_URL}/me/messages/{message_id}'
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_latest_message(self):
        """Get the most recent email message from inbox"""
        url = f'{self.BASE_URL}/me/mailFolders/inbox/messages'
        params = {
            '$top': 1,
            '$orderby': 'receivedDateTime desc'
        }
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        messages = response.json().get('value', [])
        return messages[0] if messages else None
    
    def create_reply_draft(self, message_id, reply_content):
        """Create a reply draft for a message"""
        # First, create the reply
        url = f'{self.BASE_URL}/me/messages/{message_id}/createReply'
        response = requests.post(url, headers=self._get_headers())
        response.raise_for_status()
        draft = response.json()
        
        # Update the draft with our content
        draft_id = draft['id']
        update_url = f'{self.BASE_URL}/me/messages/{draft_id}'
        
        update_data = {
            'body': {
                'contentType': 'HTML',
                'content': reply_content
            }
        }
        
        response = requests.patch(update_url, headers=self._get_headers(), json=update_data)
        response.raise_for_status()
        
        return response.json()
    
    def subscribe_to_inbox(self, notification_url, expiration_datetime):
        """Create a subscription to inbox changes"""
        url = f'{self.BASE_URL}/subscriptions'
        
        subscription_data = {
            'changeType': 'created',
            'notificationUrl': notification_url,
            'resource': '/me/mailFolders/inbox/messages',
            'expirationDateTime': expiration_datetime,
            'clientState': 'SecretClientState'  # Used to verify notifications
        }
        
        response = requests.post(url, headers=self._get_headers(), json=subscription_data)
        response.raise_for_status()
        
        return response.json()
    
    def renew_subscription(self, subscription_id, expiration_datetime):
        """Renew an existing subscription"""
        url = f'{self.BASE_URL}/subscriptions/{subscription_id}'
        
        update_data = {
            'expirationDateTime': expiration_datetime
        }
        
        response = requests.patch(url, headers=self._get_headers(), json=update_data)
        response.raise_for_status()
        
        return response.json()
    
    def delete_subscription(self, subscription_id):
        """Delete a subscription"""
        url = f'{self.BASE_URL}/subscriptions/{subscription_id}'
        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return True

# Singleton instance
graph_client = GraphClient()
