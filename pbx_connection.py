"""
Gestione connessione SSH al centralino PBX
"""
import paramiko
import time
import logging
from datetime import datetime
from config import PBX_CONFIG

class PBXConnection:
    def __init__(self, config=None):
        self.config = config or PBX_CONFIG
        self.ssh_client = None
        self.connected = False
        self.last_connection_time = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Stabilisce la connessione SSH al centralino PBX"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connessione SSH
            self.ssh_client.connect(
                hostname=self.config['host'],
                port=self.config['port'],
                username=self.config['username'],
                password=self.config['password'],
                timeout=self.config['timeout']
            )
            
            self.connected = True
            self.last_connection_time = datetime.now()
            self.logger.info(f"Connessione SSH stabilita con {self.config['host']}")
            return True
            
        except paramiko.AuthenticationException:
            self.logger.error("Errore di autenticazione SSH")
            return False
        except paramiko.SSHException as e:
            self.logger.error(f"Errore SSH: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Errore di connessione: {e}")
            return False
    
    def disconnect(self):
        """Chiude la connessione SSH"""
        if self.ssh_client:
            self.ssh_client.close()
            self.connected = False
            self.logger.info("Connessione SSH chiusa")
    
    def is_connected(self):
        """Verifica se la connessione è attiva"""
        if not self.connected or not self.ssh_client:
            return False
        
        try:
            # Testa la connessione con un comando semplice
            stdin, stdout, stderr = self.ssh_client.exec_command("echo 'test'")
            return stdout.channel.recv_exit_status() == 0
        except:
            self.connected = False
            return False
    
    def execute_command(self, command):
        """Esegue un comando sul centralino PBX"""
        if not self.is_connected():
            if not self.connect():
                return None, "Errore di connessione"
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            # Legge l'output
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            # Verifica il codice di uscita
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code == 0:
                self.logger.info(f"Comando eseguito: {command}")
                return output, None
            else:
                self.logger.error(f"Errore comando: {error}")
                return None, error
                
        except Exception as e:
            self.logger.error(f"Errore nell'esecuzione del comando: {e}")
            return None, str(e)
    
    def make_call(self, room_number, audio_file_path=None):
        """Effettua una chiamata alla camera specificata"""
        try:
            # Comando per effettuare la chiamata (da adattare al centralino specifico)
            # Esempio per centralini basati su Asterisk
            if audio_file_path:
                command = f"asterisk -rx 'originate Local/{room_number}@internal extension {room_number}@internal'"
            else:
                command = f"asterisk -rx 'originate Local/{room_number}@internal extension {room_number}@internal'"
            
            output, error = self.execute_command(command)
            
            if error:
                return False, f"Errore nella chiamata: {error}"
            
            self.logger.info(f"Chiamata effettuata alla camera {room_number}")
            return True, "Chiamata effettuata con successo"
            
        except Exception as e:
            self.logger.error(f"Errore nella chiamata alla camera {room_number}: {e}")
            return False, str(e)
    
    def play_audio(self, room_number, audio_file_path):
        """Riproduce un file audio durante la chiamata"""
        try:
            # Comando per riprodurre audio (da adattare al centralino specifico)
            command = f"asterisk -rx 'playback {audio_file_path}'"
            
            output, error = self.execute_command(command)
            
            if error:
                return False, f"Errore nella riproduzione audio: {error}"
            
            self.logger.info(f"Audio riprodotto per camera {room_number}: {audio_file_path}")
            return True, "Audio riprodotto con successo"
            
        except Exception as e:
            self.logger.error(f"Errore nella riproduzione audio: {e}")
            return False, str(e)
    
    def hangup_call(self, room_number):
        """Termina la chiamata alla camera specificata"""
        try:
            # Comando per terminare la chiamata
            command = f"asterisk -rx 'hangup {room_number}'"
            
            output, error = self.execute_command(command)
            
            if error:
                return False, f"Errore nella terminazione chiamata: {error}"
            
            self.logger.info(f"Chiamata terminata per camera {room_number}")
            return True, "Chiamata terminata con successo"
            
        except Exception as e:
            self.logger.error(f"Errore nella terminazione chiamata: {e}")
            return False, str(e)
    
    def get_call_status(self, room_number):
        """Ottiene lo status della chiamata per una camera"""
        try:
            # Comando per verificare lo status della chiamata
            command = f"asterisk -rx 'core show channels'"
            
            output, error = self.execute_command(command)
            
            if error:
                return None, f"Errore nel controllo status: {error}"
            
            # Cerca la camera nell'output
            if room_number in output:
                return "active", None
            else:
                return "inactive", None
                
        except Exception as e:
            self.logger.error(f"Errore nel controllo status chiamata: {e}")
            return None, str(e)
    
    def test_connection(self):
        """Testa la connessione al centralino"""
        try:
            if not self.connect():
                return False, "Impossibile connettersi al centralino"
            
            # Esegue un comando di test
            output, error = self.execute_command("echo 'PBX Connection Test'")
            
            if error:
                return False, f"Errore nel test: {error}"
            
            self.logger.info("Test connessione PBX completato con successo")
            return True, "Connessione testata con successo"
            
        except Exception as e:
            self.logger.error(f"Errore nel test connessione: {e}")
            return False, str(e)
        finally:
            self.disconnect()
    
    def get_system_info(self):
        """Ottiene informazioni sul sistema PBX"""
        try:
            if not self.is_connected():
                if not self.connect():
                    return None, "Errore di connessione"
            
            # Comandi per ottenere informazioni di sistema
            commands = {
                "version": "asterisk -rx 'core show version'",
                "uptime": "asterisk -rx 'core show uptime'",
                "channels": "asterisk -rx 'core show channels'",
                "extensions": "asterisk -rx 'dialplan show'"
            }
            
            info = {}
            for key, command in commands.items():
                output, error = self.execute_command(command)
                if not error:
                    info[key] = output
                else:
                    info[key] = f"Errore: {error}"
            
            return info, None
            
        except Exception as e:
            self.logger.error(f"Errore nel recupero info sistema: {e}")
            return None, str(e)

class PBXManager:
    """Manager per la gestione delle operazioni PBX"""
    
    def __init__(self):
        self.pbx = PBXConnection()
        self.active_calls = {}  # Traccia le chiamate attive
    
    def start_alarm_call(self, room_number, audio_file_path=None):
        """Avvia una chiamata di sveglia"""
        try:
            # Effettua la chiamata
            success, message = self.pbx.make_call(room_number, audio_file_path)
            
            if success:
                # Registra la chiamata attiva
                self.active_calls[room_number] = {
                    'start_time': datetime.now(),
                    'audio_file': audio_file_path,
                    'status': 'ringing'
                }
                
                # Se c'è un file audio, lo riproduce
                if audio_file_path:
                    time.sleep(2)  # Attende che la chiamata si stabilisca
                    self.pbx.play_audio(room_number, audio_file_path)
                
                return True, "Chiamata di sveglia avviata"
            else:
                return False, message
                
        except Exception as e:
            return False, f"Errore nell'avvio chiamata sveglia: {e}"
    
    def end_alarm_call(self, room_number):
        """Termina una chiamata di sveglia"""
        try:
            if room_number in self.active_calls:
                # Termina la chiamata
                success, message = self.pbx.hangup_call(room_number)
                
                if success:
                    # Rimuove dalla lista delle chiamate attive
                    del self.active_calls[room_number]
                    return True, "Chiamata di sveglia terminata"
                else:
                    return False, message
            else:
                return False, "Nessuna chiamata attiva per questa camera"
                
        except Exception as e:
            return False, f"Errore nella terminazione chiamata: {e}"
    
    def get_active_calls(self):
        """Ottiene la lista delle chiamate attive"""
        return self.active_calls.copy()
    
    def cleanup_old_calls(self, max_duration_minutes=30):
        """Pulisce le chiamate vecchie"""
        current_time = datetime.now()
        to_remove = []
        
        for room, call_info in self.active_calls.items():
            duration = (current_time - call_info['start_time']).total_seconds() / 60
            if duration > max_duration_minutes:
                to_remove.append(room)
        
        for room in to_remove:
            self.end_alarm_call(room)

if __name__ == "__main__":
    # Test del modulo
    pbx = PBXConnection()
    success, message = pbx.test_connection()
    print(f"Test connessione: {success} - {message}")
