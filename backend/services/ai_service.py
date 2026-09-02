"""
OpenAI / Claude AI Service
Mesajlara AI yanıtları oluşturur.
"""

import openai
import logging
import os

logger = logging.getLogger(__name__)

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(user_message: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Kullanıcının mesajına AI yanıtı oluşturur.
    
    Args:
        user_message: Kullanıcının girdisi
        model: Kullanılacak model (gpt-3.5-turbo, gpt-4, vb.)
    
    Returns:
        str: AI'nin yanıtı
    """
    try:
        logger.info(f"Getting AI response for: {user_message[:50]}...")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """Siz yardımcı, dostça ve bilgili bir AI asistan'sınız.
                    Kullanıcının sorularına Türkçe'de açık, kısa ve faydalı yanıtlar verin.
                    Eğer bilmiyorsanız, açıkça söyleyin."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"AI Response: {ai_response[:50]}...")
        
        return ai_response
    
    except openai.error.AuthenticationError:
        logger.error("Invalid OpenAI API key")
        raise Exception("OpenAI authentication failed. Check your API key.")
    except openai.error.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        raise Exception("Too many requests. Please try again later.")
    except Exception as e:
        logger.error(f"AI service error: {str(e)}")
        raise Exception(f"Failed to get AI response: {str(e)}")

def get_ai_response_stream(user_message: str, model: str = "gpt-3.5-turbo"):
    """
    AI yanıtını streaming olarak oluşturur (gerçek zamanlı)
    
    Args:
        user_message: Kullanıcının girdisi
        model: Kullanılacak model
    
    Yields:
        str: Yanıtın parçaları
    """
    try:
        logger.info(f"Getting streaming AI response for: {user_message[:50]}...")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """Siz yardımcı, dostça ve bilgili bir AI asistan'sınız.
                    Kullanıcının sorularına Türkçe'de açık, kısa ve faydalı yanıtlar verin."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=500,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    except Exception as e:
        logger.error(f"Streaming AI error: {str(e)}")
        raise Exception(f"Failed to get streaming AI response: {str(e)}")

def get_conversation_response(conversation_history: list, model: str = "gpt-3.5-turbo") -> str:
    """
    Konuşma geçmişini dikkate alarak yanıt oluşturur.
    
    Args:
        conversation_history: Önceki mesajların listesi
        model: Kullanılacak model
    
    Returns:
        str: AI'nin yanıtı
    """
    try:
        logger.info("Getting response with conversation history...")
        
        # Mesaj geçmişini format et
        messages = [
            {
                "role": "system",
                "content": """Siz yardımcı, dostça ve bilgili bir AI asistan'sınız.
                Konuşma bağlamını dikkate alarak Türkçe'de yanıtlar verin."""
            }
        ]
        messages.extend(conversation_history)
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"Response: {ai_response[:50]}...")
        
        return ai_response
    
    except Exception as e:
        logger.error(f"Conversation error: {str(e)}")
        raise Exception(f"Failed to get conversation response: {str(e)}")
