"""
Google Cloud Text-to-Speech Service
Metni konuşma sesine çevirir.
"""

from google.cloud import texttospeech_v1
import logging

logger = logging.getLogger(__name__)

def synthesize_text(text: str, language_code: str = "tr-TR", voice_name: str = "tr-TR-Neural2-C") -> bytes:
    """
    Metni konuşma sesine çevirir.
    
    Args:
        text: Sese çevrilecek metin
        language_code: Dil kodu (varsayılan: Türkçe)
        voice_name: Ses adı (varsayılan: Türkçe kadın sesi)
    
    Returns:
        bytes: MP3 ses dosyası
    """
    try:
        client = texttospeech_v1.TextToSpeechClient()
        
        # Metin input
        synthesis_input = texttospeech_v1.SynthesisInput(text=text)
        
        # Ses ayarları
        voice = texttospeech_v1.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        )
        
        # Audio konfigürasyonu
        audio_config = texttospeech_v1.AudioConfig(
            audio_encoding=texttospeech_v1.AudioEncoding.MP3,
            speaking_rate=1.0,  # Normal hız
        )
        
        # Synthesize request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        logger.info(f"Synthesized {len(text)} characters to audio")
        
        return response.audio_content
    
    except Exception as e:
        logger.error(f"Synthesis error: {str(e)}")
        raise Exception(f"Text-to-Speech failed: {str(e)}")

def synthesize_with_ssml(ssml: str, language_code: str = "tr-TR", voice_name: str = "tr-TR-Neural2-C") -> bytes:
    """
    SSML formatında metni sese çevirir (daha detaylı kontrol).
    
    Args:
        ssml: SSML formatında metin
        language_code: Dil kodu
        voice_name: Ses adı
    
    Returns:
        bytes: MP3 ses dosyası
    """
    try:
        client = texttospeech_v1.TextToSpeechClient()
        
        # SSML input
        synthesis_input = texttospeech_v1.SynthesisInput(ssml=ssml)
        
        # Ses ayarları
        voice = texttospeech_v1.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        )
        
        # Audio konfigürasyonu
        audio_config = texttospeech_v1.AudioConfig(
            audio_encoding=texttospeech_v1.AudioEncoding.MP3,
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        logger.info("SSML synthesized to audio")
        
        return response.audio_content
    
    except Exception as e:
        logger.error(f"SSML Synthesis error: {str(e)}")
        raise Exception(f"SSML Text-to-Speech failed: {str(e)}")

def list_available_voices(language_code: str = "tr-TR") -> list:
    """
    Kullanılabilir sesleri listeler.
    
    Args:
        language_code: Dil kodu
    
    Returns:
        list: Kullanılabilir sesler
    """
    try:
        client = texttospeech_v1.TextToSpeechClient()
        response = client.list_voices()
        
        voices = [
            {
                "name": voice.name,
                "language_codes": voice.language_codes,
                "ssml_gender": voice.ssml_gender.name,
                "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
            }
            for voice in response.voices
            if language_code in voice.language_codes
        ]
        
        logger.info(f"Found {len(voices)} voices for {language_code}")
        
        return voices
    
    except Exception as e:
        logger.error(f"List voices error: {str(e)}")
        raise Exception(f"Failed to list voices: {str(e)}")
