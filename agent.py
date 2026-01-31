from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class HoneypotAgent:
    def __init__(self):
        """Initialize Groq client"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.conversation_history = []
    
    def set_persona(self, persona_prompt: str):
        """Set the AI persona"""
        self.persona = persona_prompt
        self.conversation_history = []
    
    def chat(self, user_message: str) -> str:
        """
        Send message to Groq and get response
        
        Args:
            user_message: Message from scammer
            
        Returns:
            AI agent response
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Create messages with system prompt
            messages = [
                {
                    "role": "system",
                    "content": self.persona
                }
            ] + self.conversation_history
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200,
                top_p=1,
                stream=False
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []