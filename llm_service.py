import config
import google.generativeai as genai

class LLMService:
    """Service for generating email replies using Google Gemini API"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    def generate_reply(self, email_subject, email_body, sender_email):
        """Generate a reply to an email using Gemini"""
        
        prompt = self._create_prompt(email_subject, email_body, sender_email)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 1000,
                }
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error generating reply with Gemini: {str(e)}")
            raise
    
    def _create_prompt(self, subject, body, sender):
        """Create a prompt for Gemini from file"""
        try:
            import os
            # Handle path for both local and Lambda environment
            base_path = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(base_path, 'prompts', 'email_reply.txt')
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Fill in the template
            return template.format(
                sender=sender,
                subject=subject,
                body=body
            )
        except Exception as e:
            print(f"Error reading prompt file: {e}")
            # Fallback prompt just in case
            return f"""
            You are an AI assistant. Please draft a reply to this email:
            From: {sender}
            Subject: {subject}
            Body: {body}
            """

# Singleton instance
llm_service = LLMService()
