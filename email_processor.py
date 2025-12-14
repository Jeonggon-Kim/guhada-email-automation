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
            conversation_id = message.get('conversationId')
            
            # Extract email details
            subject = message.get('subject', 'No Subject')
            sender = message.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')
            body_content = message.get('body', {}).get('content', '')
            body_type = message.get('body', {}).get('contentType', 'Text')
            
            # Convert HTML to plain text
            if body_type == 'HTML':
                plain_body = self._strip_html(body_content)
            else:
                plain_body = body_content
            
            # Fetch thread history
            thread_history = ""
            if conversation_id:
                try:
                    print(f"Fetching thread history for conversation: {conversation_id}")
                    threads = graph_client.get_conversation_threads(conversation_id)
                    
                    # Format threads for LLM
                    history_list = []
                    for msg in threads:
                        # Skip the current message to avoid duplication in history
                        if msg.get('id') == message_id:
                            continue
                            
                        msg_sender = msg.get('from', {}).get('emailAddress', {}).get('name', 'Unknown')
                        msg_content = msg.get('body', {}).get('content', '')
                        clean_content = self._strip_html(msg_content)
                        # Truncate very long messages
                        if len(clean_content) > 1000:
                            clean_content = clean_content[:1000] + "..."
                            
                        date = msg.get('receivedDateTime', '').split('T')[0]
                        history_list.append(f"--- Message from {msg_sender} on {date} ---\n{clean_content}")
                    
                    thread_history = "\n\n".join(history_list)
                except Exception as e:
                    print(f"Warning: Failed to fetch thread history: {e}")
            
            print(f"Email from: {sender}")
            print(f"Subject: {subject}")
            
            # Generate reply using LLM
            print("Generating reply with LLM...")
            reply_content = llm_service.generate_reply(subject, plain_body, sender, thread_history)
            
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
