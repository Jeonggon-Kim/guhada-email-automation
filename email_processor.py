import html
from graph_client import graph_client
from llm_service import llm_service

class EmailProcessor:
    """Processes incoming emails and generates draft replies"""
    
    def process_email(self, message_id):
        """
        Process an incoming email:
        1. Fetch email details
        2. Generate reply using LLM
        3. Create draft in Outlook
        """
        try:
            print(f"Processing email: {message_id}")
            
            # Get the email message
            message = graph_client.get_message(message_id)
            
            # Extract email details
            subject = message.get('subject', 'No Subject')
            sender = message.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')
            body_content = message.get('body', {}).get('content', '')
            body_type = message.get('body', {}).get('contentType', 'Text')
            
            # Convert HTML to plain text if needed for better LLM processing
            if body_type == 'HTML':
                # Strip HTML tags for LLM input
                plain_body = self._strip_html(body_content)
            else:
                plain_body = body_content
            
            print(f"Email from: {sender}")
            print(f"Subject: {subject}")
            
            # Generate reply using LLM
            print("Generating reply with LLM...")
            reply_content = llm_service.generate_reply(subject, plain_body, sender)
            
            # Create draft reply in Outlook
            print("Creating draft reply in Outlook...")
            draft = graph_client.create_reply_draft(message_id, reply_content)
            
            print(f"✓ Draft created successfully! Draft ID: {draft['id']}")
            
            return {
                'success': True,
                'message_id': message_id,
                'draft_id': draft['id'],
                'subject': subject,
                'sender': sender
            }
            
        except Exception as e:
            print(f"✗ Error processing email: {str(e)}")
            return {
                'success': False,
                'message_id': message_id,
                'error': str(e)
            }
    
    def _strip_html(self, html_content):
        """Strip HTML tags from content"""
        # Simple HTML stripping (you might want to use BeautifulSoup for better results)
        import re
        text = re.sub('<[^<]+?>', '', html_content)
        return html.unescape(text)

# Singleton instance
email_processor = EmailProcessor()
