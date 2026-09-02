"""
Google Cloud Speech-to-Text Service
Ses dosyalarını metne çevirir.
"""

from google.cloud import speech_v1
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

def transcribe_audio(audio_content: bytes, language_code: str = "tr-TR") -> dict:
    """
    Ses dosyasını metne çevirir.
    
    Args:
        audio_content: Ses dosyasının byte içeriği
        language_code: Dil kodu (varsayılan: Türkçe)
    
    Returns:
        dict: {"text": "...", "confidence": 0.95}
    """
    try:
        client = speech_v1.SpeechClient()
        
        # Audio konfigürasyonu
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        # Audio dosyası
        audio = speech_v1.RecognitionAudio(content=audio_content)
        
        # Recognize request
        response = client.recognize(config=config, audio=audio)
        
        # Sonuçları işle
        if response.results:
            # İlk sonuç (en yüksek güven)
            result = response.results[0]
            
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence
                
                logger.info(f"Transcribed: {transcript} (confidence: {confidence})")
                
                return {
                    "text": transcript,
                    "confidence": confidence
                }
        
        logger.warning("No transcription results found")
        return {"text": "", "confidence": 0}
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise Exception(f"Speech-to-Text failed: {str(e)}")

def transcribe_audio_streaming(audio_stream, language_code: str = "tr-TR"):
    """
    Streaming audio'yu metne çevirir (gerçek zamanlı)
    
    Args:
        audio_stream: Ses stream'i
        language_code: Dil kodu
    
    Yields:
        str: Kısmi/tam transcription sonuçları
    """
    try:
        client = speech_v1.SpeechClient()
        
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        streaming_config = speech_v1.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )
        
        # Ses stream'ini gönder
        requests = (
            speech_v1.StreamingRecognizeRequest(audio_content=chunk)
            for chunk in audio_stream
        )
        
        responses = client.streaming_recognize(streaming_config, requests)
        
        for response in responses:
            if not response.results:
                continue
            
            result = response.results[0]
            transcript = result.alternatives[0].transcript
            
            if result.is_final:
                logger.info(f"Final: {transcript}")
                yield {"text": transcript, "is_final": True}
            else:
                logger.debug(f"Interim: {transcript}")
                yield {"text": transcript, "is_final": False}
    
    except Exception as e:
        logger.error(f"Streaming transcription error: {str(e)}")
        raise Exception(f"Streaming transcription failed: {str(e)}")
