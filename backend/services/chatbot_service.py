import os
import requests
from typing import Optional
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class ChatbotService:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.enabled = self.api_key is not None
    
    def chat_about_preferences(self, user_message: str, conversation_history: list = None, retries: int = 3) -> str:
        """
        Chat with users about their movie preferences using OpenRouter with retry logic
        """
        if not self.enabled:
            return "AI chat is not available. Please check your OpenRouter API key."
        
        for attempt in range(retries):
            try:
                messages = [
                    {
                        "role": "system",
                        "content": "You are a friendly movie recommendation assistant. Help users discover movies they'll love by understanding their preferences through conversation. Keep responses concise and helpful."
                    }
                ]
                
                # Add conversation history if provided
                if conversation_history:
                    messages.extend(conversation_history)
                
                messages.append({"role": "user", "content": user_message})
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Movie Recommendation System"
                }
                
                payload = {
                    "model": "meta-llama/llama-3.2-3b-instruct:free",  # Using free model
                    "messages": messages,
                    "max_tokens": 250,
                    "temperature": 0.8
                }
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"OpenRouter API error: {response.status_code} - {response.text}")
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return "I'm having trouble responding right now. Please try again."
            
            except Exception as e:
                print(f"Chatbot error: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return "An error occurred. Please try again."
        
        return "I'm experiencing high load. Please try again in a moment."
