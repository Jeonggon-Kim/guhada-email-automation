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
        """Create a prompt for Gemini"""
        return f"""You are an AI assistant helping to draft professional email replies for K Glowing company.

Email Details:
- From: {sender}
- Subject: {subject}
- Body:
{body}

Please generate a professional, courteous, and helpful reply to this email. 
The reply should:
1. Address the sender's concerns or questions
2. Be concise and clear
3. Maintain a professional tone appropriate for K Glowing
4. Include appropriate greetings and closing

Generate ONLY the email body content (no subject line). Format the response in HTML for better presentation.
"""

# Singleton instance
llm_service = LLMService()
