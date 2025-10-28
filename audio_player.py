"""
Riproduzione audio per messaggi di sveglia
"""
import pygame
import os
import logging
from logger import get_logger

class AudioPlayer:
    """Gestisce la riproduzione di file audio"""
    
    def __init__(self):
        self.logger = get_logger('audio_player')
        self.initialized = False
        self.current_playing = None
        
        try:
            # Inizializza pygame mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self.initialized = True
            self.logger.info("Audio player inizializzato con successo")
        except Exception as e:
            self.logger.error(f"Errore inizializzazione pygame mixer: {e}")
            self.initialized = False
    
    def play(self, audio_file_path):
        """
        Riproduce un file audio
        
        Args:
            audio_file_path: Percorso completo al file audio
            
        Returns:
            (success, message): Tupla con successo e messaggio
        """
        if not self.initialized:
            return False, "Audio player non inizializzato"
        
        if not os.path.exists(audio_file_path):
            self.logger.error(f"File audio non trovato: {audio_file_path}")
            return False, f"File non trovato: {audio_file_path}"
        
        try:
            self.logger.info(f"Riproduzione audio: {audio_file_path}")
            
            # Ferma eventuale audio in riproduzione
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Carica e riproduci
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()
            
            self.current_playing = audio_file_path
            self.logger.info(f"Riproduzione avviata: {os.path.basename(audio_file_path)}")
            
            return True, "Riproduzione avviata"
            
        except Exception as e:
            self.logger.error(f"Errore riproduzione audio: {e}")
            return False, f"Errore: {str(e)}"
    
    def stop(self):
        """Ferma la riproduzione audio"""
        if not self.initialized:
            return False, "Audio player non inizializzato"
        
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                self.logger.info("Riproduzione fermata")
                self.current_playing = None
                return True, "Riproduzione fermata"
            else:
                return False, "Nessun audio in riproduzione"
        except Exception as e:
            self.logger.error(f"Errore stop audio: {e}")
            return False, f"Errore: {str(e)}"
    
    def is_playing(self):
        """Verifica se un audio è in riproduzione"""
        if not self.initialized:
            return False
        
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False
    
    def get_volume(self):
        """Ottiene il volume corrente (0.0 - 1.0)"""
        if not self.initialized:
            return 0.0
        
        try:
            return pygame.mixer.music.get_volume()
        except:
            return 0.0
    
    def set_volume(self, volume):
        """
        Imposta il volume (0.0 - 1.0)
        
        Args:
            volume: Volume da 0.0 a 1.0
        """
        if not self.initialized:
            return False
        
        try:
            # Clamp volume tra 0.0 e 1.0
            volume = max(0.0, min(1.0, float(volume)))
            pygame.mixer.music.set_volume(volume)
            self.logger.info(f"Volume impostato a: {volume:.2f}")
            return True
        except Exception as e:
            self.logger.error(f"Errore impostazione volume: {e}")
            return False
    
    def cleanup(self):
        """Pulisce le risorse audio"""
        if self.initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                self.logger.info("Audio player chiuso")
            except:
                pass

# Istanza globale per riuso
_audio_player_instance = None

def get_audio_player():
    """Ottiene l'istanza singleton dell'audio player"""
    global _audio_player_instance
    if _audio_player_instance is None:
        _audio_player_instance = AudioPlayer()
    return _audio_player_instance

