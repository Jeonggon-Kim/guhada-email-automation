import sys
import os
# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, redirect
from auth_provider import auth_provider
from email_processor import email_processor
import config

app = Flask(__name__)

# Store validation tokens for webhook verification
validation_tokens = {}

@app.route('/')
def home():
    """Home page with authentication status"""
    is_authenticated = auth_provider.is_authenticated()
    
    if is_authenticated:
        return """
        <h1>Outlook Email Automation</h1>
        <p>✓ Authenticated and ready!</p>
        <p>The webhook is listening for incoming emails.</p>
        
        <div style="margin: 20px 0; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
            <h3>🧪 Manual Test</h3>
            <p>Click the button below to process the most recent email in your inbox immediately:</p>
            <button onclick="processLatest()" style="padding: 10px 20px; background-color: #0078d4; color: white; border: none; border-radius: 4px; cursor: pointer;">Process Latest Email</button>
            <p id="result" style="margin-top: 10px;"></p>
        </div>

        <script>
        function processLatest() {
            document.getElementById('result').innerText = 'Processing...';
            fetch('/test/latest')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('result').innerText = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    document.getElementById('result').innerText = 'Error: ' + error;
                });
        }
        </script>

        <p>When a new email arrives, the system will:</p>
        <ol>
            <li>Receive webhook notification</li>
            <li>Fetch the email content</li>
            <li>Generate a reply using AI</li>
            <li>Save the reply as a draft in Outlook</li>
        </ol>
        """
    else:
        auth_url = auth_provider.get_auth_url()
        return f"""
        <h1>Outlook Email Automation</h1>
        <p>Please authenticate to start:</p>
        <a href="{auth_url}">Login with Microsoft</a>
        """

@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        return "Error: No authorization code received", 400
    
    try:
        auth_provider.acquire_token_by_code(code)
        return redirect('/')
    except Exception as e:
        return f"Authentication error: {str(e)}", 500

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """
    Handle Microsoft Graph webhook notifications
    
    Microsoft sends two types of requests:
    1. Validation request (GET/POST with validationToken)
    2. Notification request (POST with change notifications)
    """
    
    # Handle validation request
    if request.args.get('validationToken'):
        validation_token = request.args.get('validationToken')
        print(f"Webhook validation request received")
        # Return the validation token in plain text
        return validation_token, 200, {'Content-Type': 'text/plain'}
    
    # Handle notification request
    if request.method == 'POST':
        try:
            data = request.json
            
            # Verify client state
            if data.get('value'):
                for notification in data['value']:
                    client_state = notification.get('clientState')
                    
                    # Verify this is from Microsoft (check client state)
                    if client_state != 'SecretClientState':
                        print(f"Invalid client state: {client_state}")
                        continue
                    
                    # Get the resource data
                    resource_data = notification.get('resourceData', {})
                    message_id = resource_data.get('id')
                    
                    if message_id:
                        print(f"New email notification received: {message_id}")
                        
                        # Process the email asynchronously (in production, use a queue)
                        result = email_processor.process_email(message_id)
                        
                        if result['success']:
                            print(f"✓ Successfully processed email and created draft")
                        else:
                            print(f"✗ Failed to process email: {result.get('error')}")
            
            # Always return 202 Accepted to acknowledge receipt
            return '', 202
            
        except Exception as e:
            print(f"Error handling webhook: {str(e)}")
            # Still return 202 to avoid Microsoft retrying
            return '', 202
    
    return 'Webhook endpoint', 200

@app.route('/test/process/<message_id>')
def test_process(message_id):
    """Test endpoint to manually process an email"""
    result = email_processor.process_email(message_id)
    return jsonify(result)

@app.route('/test/latest')
def test_latest():
    """Test endpoint to process the most recent email"""
    from graph_client import graph_client
    
    # Get latest message
    message = graph_client.get_latest_message()
    
    if not message:
        return jsonify({'success': False, 'error': 'No emails found in inbox'})
    
    print(f"Processing latest email: {message['subject']} ({message['id']})")
    
    # Process it
    result = email_processor.process_email(message['id'])
    return jsonify(result)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'authenticated': auth_provider.is_authenticated()
    })

if __name__ == '__main__':
    print(f"Starting Outlook Email Automation Server...")
    print(f"Server running on http://localhost:{config.PORT}")
    print(f"Webhook URL: {config.WEBHOOK_URL}/webhook")
    
    if not auth_provider.is_authenticated():
        print("\n⚠ Not authenticated yet. Please visit http://localhost:{} to login".format(config.PORT))
    else:
        print("\n✓ Authenticated and ready!")
    
    app.run(host='0.0.0.0', port=config.PORT, debug=True)
