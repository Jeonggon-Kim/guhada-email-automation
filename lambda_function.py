import json
import os
import logging
from auth_provider_aws import aws_auth_provider
from graph_client import GraphClient
from email_processor import EmailProcessor

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services with AWS auth provider
import graph_client as graph_client_module
graph_client = graph_client_module.graph_client
# Inject AWS auth provider
graph_client.auth_provider = aws_auth_provider

# Initialize email processor
email_processor = EmailProcessor()
# Ensure email processor uses the configured graph client
email_processor.graph_client = graph_client

def lambda_handler(event, context):
    """
    AWS Lambda Handler
    Handles:
    1. Webhook validation (GET)
    2. Email notifications (POST)
    3. Scheduled subscription renewal (EventBridge)
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # 1. Handle Scheduled Event (EventBridge) -> Renew Subscription
    if event.get('source') == 'aws.events':
        logger.info("Handling scheduled event: Renewing subscription")
        try:
            from datetime import datetime, timedelta
            import config
            
            expiration = datetime.utcnow() + timedelta(days=2) # Renew for 2 days
            expiration_str = expiration.strftime('%Y-%m-%dT%H:%M:%S.0000000Z')
            notification_url = os.environ.get('WEBHOOK_URL') # Get from env var
            
            if not notification_url:
                raise Exception("WEBHOOK_URL environment variable is missing")
                
            # Smart Renewal Logic
            # 1. List existing subscriptions
            existing_subs = graph_client.list_subscriptions()
            target_sub = None
            
            # 2. Find subscription with matching URL
            for sub in existing_subs:
                if sub.get('notificationUrl') == notification_url:
                    target_sub = sub
                    break
            
            if target_sub:
                # 3a. Renew existing
                logger.info(f"Found existing subscription {target_sub['id']}, renewing...")
                sub = graph_client.renew_subscription(target_sub['id'], expiration_str)
                logger.info(f"Subscription renewed: {sub['id']}")
                return {'statusCode': 200, 'body': f"Renewed: {sub['id']}"}
            else:
                # 3b. Create new
                logger.info("No existing subscription found, creating new...")
                sub = graph_client.subscribe_to_inbox(notification_url, expiration_str)
                logger.info(f"Subscription created: {sub['id']}")
                return {'statusCode': 200, 'body': f"Created: {sub['id']}"}
            
        except Exception as e:
            logger.error(f"Failed to renew subscription: {str(e)}")
            return {'statusCode': 500, 'body': str(e)}

    # 2. Handle HTTP Requests (API Gateway)
    # Support both API Gateway V1 and V2 formats
    http_method = event.get('httpMethod')
    if not http_method and 'requestContext' in event:
        http_method = event['requestContext'].get('http', {}).get('method')
        
    query_params = event.get('queryStringParameters') or {}
    body = event.get('body')
    
    # 2a. Webhook Validation (GET or POST with validationToken)
    validation_token = query_params.get('validationToken')
    if validation_token:
        logger.info(f"Handling validation request: {validation_token}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': validation_token
        }
    
    # 2b. Email Notification (POST)
    if http_method == 'POST':
        try:
            if not body:
                return {'statusCode': 400, 'body': 'No body'}
                
            data = json.loads(body) if isinstance(body, str) else body
            
            if data.get('value'):
                for notification in data['value']:
                    # Verify client state
                    if notification.get('clientState') != 'SecretClientState':
                        logger.warning("Invalid client state")
                        continue
                        
                    resource_data = notification.get('resourceData', {})
                    message_id = resource_data.get('id')
                    
                    if message_id:
                        logger.info(f"Processing email: {message_id}")
                        result = email_processor.process_email(message_id)
                        logger.info(f"Process result: {result}")
            
            return {'statusCode': 202, 'body': 'Accepted'}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return {'statusCode': 500, 'body': str(e)}
            
    return {'statusCode': 400, 'body': 'Invalid request'}
