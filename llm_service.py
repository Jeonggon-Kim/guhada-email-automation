import config
import google.generativeai as genai

class LLMService:
    """Service for generating email replies using Google Gemini API"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    def generate_reply(self, email_subject, email_body, sender_email, thread_history=""):
        """Generate a reply to an email using Gemini"""
        
        prompt = self._create_prompt(email_subject, email_body, sender_email, thread_history)
        
        # Log the full prompt for debugging
        print("\n" + "="*30 + " FULL PROMPT TO GEMINI " + "="*30)
        print(prompt)
        print("="*83 + "\n")
        
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
    
    def _create_prompt(self, subject, body, sender, thread_history=""):
        """Create a prompt for Gemini"""
        try:
            from prompts.email_reply import EMAIL_REPLY_PROMPT
            
            # Fill in the template
            return EMAIL_REPLY_PROMPT.format(
                sender=sender,
                subject=subject,
                body=body,
                thread_history=thread_history if thread_history else "No previous conversation."
            )
        except Exception as e:
            print(f"Error creating prompt: {e}")
            # Fallback prompt just in case
            return f"""
            You are an AI assistant. Please draft a reply to this email:
            From: {sender}
            Subject: {subject}
            Body: {body}
            """

# Singleton instance
llm_service = LLMService()
