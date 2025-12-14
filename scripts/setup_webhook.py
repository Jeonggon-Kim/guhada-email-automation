"""
Setup script to register webhook subscription with Microsoft Graph API
Run this after authenticating to start receiving email notifications
"""

from datetime import datetime, timedelta
import sys
import os
# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_client import graph_client
import config
import json

def setup_subscription():
    """Create a webhook subscription for new emails"""
    
    # Subscription expires in 3 days (max for personal accounts)
    expiration = datetime.utcnow() + timedelta(days=3)
    expiration_str = expiration.strftime('%Y-%m-%dT%H:%M:%S.0000000Z')
    
    notification_url = f"{config.WEBHOOK_URL}/webhook"
    
    print("Setting up webhook subscription...")
    print(f"Notification URL: {notification_url}")
    print(f"Expiration: {expiration_str}")
    
    try:
        subscription = graph_client.subscribe_to_inbox(
            notification_url=notification_url,
            expiration_datetime=expiration_str
        )
        
        print("\n✓ Subscription created successfully!")
        print(f"Subscription ID: {subscription['id']}")
        print(f"Resource: {subscription['resource']}")
        print(f"Change Type: {subscription['changeType']}")
        print(f"Expires: {subscription['expirationDateTime']}")
        
        # Save subscription info
        with open('subscription.json', 'w') as f:
            json.dump(subscription, f, indent=2)
        
        print("\nSubscription details saved to subscription.json")
        print("\n⚠ Remember to renew the subscription before it expires!")
        
        return subscription
        
    except Exception as e:
        print(f"\n✗ Error creating subscription: {str(e)}")
        print("\nMake sure:")
        print("1. You are authenticated (run server.py and login first)")
        print("2. Your webhook URL is publicly accessible (use ngrok)")
        print("3. The webhook endpoint can handle validation requests")
        return None

def renew_subscription(subscription_id):
    """Renew an existing subscription"""
    
    expiration = datetime.utcnow() + timedelta(days=3)
    expiration_str = expiration.strftime('%Y-%m-%dT%H:%M:%S.0000000Z')
    
    print(f"Renewing subscription: {subscription_id}")
    
    try:
        subscription = graph_client.renew_subscription(
            subscription_id=subscription_id,
            expiration_datetime=expiration_str
        )
        
        print("\n✓ Subscription renewed successfully!")
        print(f"New expiration: {subscription['expirationDateTime']}")
        
        return subscription
        
    except Exception as e:
        print(f"\n✗ Error renewing subscription: {str(e)}")
        return None

def delete_subscription(subscription_id):
    """Delete a subscription"""
    
    print(f"Deleting subscription: {subscription_id}")
    
    try:
        graph_client.delete_subscription(subscription_id)
        print("\n✓ Subscription deleted successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error deleting subscription: {str(e)}")
        return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'renew' and len(sys.argv) > 2:
            subscription_id = sys.argv[2]
            renew_subscription(subscription_id)
        elif command == 'delete' and len(sys.argv) > 2:
            subscription_id = sys.argv[2]
            delete_subscription(subscription_id)
        else:
            print("Usage:")
            print("  python setup_webhook.py              - Create new subscription")
            print("  python setup_webhook.py renew <id>   - Renew subscription")
            print("  python setup_webhook.py delete <id>  - Delete subscription")
    else:
        setup_subscription()
