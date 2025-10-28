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
    
    def make_call(self, phone_extension, audio_file_path=None):
        """Effettua una chiamata all'interno telefonico specificato"""
        try:
            # Comando per effettuare la chiamata (da adattare al centralino specifico)
            # Esempio per centralini basati su Asterisk
            command = f"asterisk -rx 'originate Local/{phone_extension}@internal extension {phone_extension}@internal'"
            
            output, error = self.execute_command(command)
            
            if error:
                return False, f"Errore nella chiamata: {error}"
            
            self.logger.info(f"Chiamata effettuata all'interno {phone_extension}")
            return True, "Chiamata effettuata con successo"
            
        except Exception as e:
            self.logger.error(f"Errore nella chiamata all'interno {phone_extension}: {e}")
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
    
    def get_sip_peers(self):
        """Ottiene la lista degli interni SIP/PJSIP configurati con il loro stato"""
        try:
            self.logger.info("Lettura interni dal centralino...")
            
            # Prova prima con SIP
            command = "asterisk -rx 'sip show peers'"
            output, error = self.execute_command(command)
            
            if error or not output or 'Unable to connect' in output:
                # Prova con PJSIP (Asterisk 12+)
                self.logger.info("SIP non disponibile, provo con PJSIP...")
                command = "asterisk -rx 'pjsip show endpoints'"
                output, error = self.execute_command(command)
                
                if error or not output:
                    return None, "Impossibile leggere gli interni dal centralino"
                
                return self._parse_pjsip_output(output), None
            
            return self._parse_sip_output(output), None
            
        except Exception as e:
            self.logger.error(f"Errore nella lettura interni: {e}")
            return None, str(e)
    
    def _parse_sip_output(self, output):
        """Parsa l'output di 'sip show peers'"""
        peers = []
        lines = output.split('\n')
        
        self.logger.info(f"Parsing SIP output ({len(lines)} righe)...")
        
        for line in lines:
            # Formato tipico: 101/101    D  A  5060  OK (15 ms)
            # o: 101/101    (Unmonitored)
            line = line.strip()
            if not line or line.startswith('Name') or line.startswith('===') or 'sip peers' in line.lower():
                continue
            
            parts = line.split()
            if len(parts) >= 1:
                # Estrae il numero interno
                peer_name = parts[0].split('/')[0].strip()
                
                # Verifica se è un numero (interno telefonico)
                if peer_name.isdigit() or peer_name.startswith('SIP/'):
                    peer_name = peer_name.replace('SIP/', '')
                    
                    # Determina lo stato (online/offline)
                    status = 'offline'
                    if 'OK' in line or 'Reachable' in line:
                        status = 'online'
                    elif 'Unreachable' in line or 'UNREACHABLE' in line:
                        status = 'offline'
                    elif 'Unmonitored' in line:
                        status = 'unmonitored'
                    
                    # Estrae latency se disponibile
                    latency = None
                    if '(' in line and 'ms' in line:
                        try:
                            latency_str = line[line.find('(')+1:line.find('ms')].strip()
                            latency = int(latency_str)
                        except:
                            pass
                    
                    peers.append({
                        'extension': peer_name,
                        'status': status,
                        'latency': latency,
                        'type': 'SIP'
                    })
        
        self.logger.info(f"Trovati {len(peers)} interni SIP")
        return peers
    
    def _parse_pjsip_output(self, output):
        """Parsa l'output di 'pjsip show endpoints'"""
        peers = []
        lines = output.split('\n')
        
        self.logger.info(f"Parsing PJSIP output ({len(lines)} righe)...")
        
        for line in lines:
            # Formato tipico: 101    Yes    No   Avail   10.0.0.15  5060
            line = line.strip()
            if not line or line.startswith('Endpoint') or line.startswith('===') or 'Objects found' in line:
                continue
            
            parts = line.split()
            if len(parts) >= 1:
                peer_name = parts[0].strip()
                
                # Verifica se è un numero (interno telefonico)
                if peer_name.isdigit():
                    # Determina lo stato
                    status = 'offline'
                    if 'Avail' in line or 'Online' in line:
                        status = 'online'
                    elif 'Unavail' in line or 'Offline' in line:
                        status = 'offline'
                    
                    peers.append({
                        'extension': peer_name,
                        'status': status,
                        'latency': None,
                        'type': 'PJSIP'
                    })
        
        self.logger.info(f"Trovati {len(peers)} interni PJSIP")
        return peers
    
    def get_extension_status(self, extension):
        """Ottiene lo stato di un singolo interno"""
        try:
            # Prova SIP
            command = f"asterisk -rx 'sip show peer {extension}'"
            output, error = self.execute_command(command)
            
            if error or 'not found' in output.lower():
                # Prova PJSIP
                command = f"asterisk -rx 'pjsip show endpoint {extension}'"
                output, error = self.execute_command(command)
                
                if error:
                    return 'unknown', None
            
            # Analizza output per determinare stato
            if 'OK' in output or 'Reachable' in output or 'Avail' in output:
                return 'online', None
            elif 'Unreachable' in output or 'Unavail' in output:
                return 'offline', None
            else:
                return 'unknown', None
                
        except Exception as e:
            self.logger.error(f"Errore nel controllo stato interno {extension}: {e}")
            return 'error', str(e)

class PBXManager:
    """Manager per la gestione delle operazioni PBX"""
    
    def __init__(self):
        self.pbx = PBXConnection()
        self.active_calls = {}  # Traccia le chiamate attive
    
    def start_alarm_call(self, phone_extension, audio_file_path=None):
        """Avvia una chiamata di sveglia"""
        try:
            # Effettua la chiamata
            success, message = self.pbx.make_call(phone_extension, audio_file_path)
            
            if success:
                # Registra la chiamata attiva
                self.active_calls[phone_extension] = {
                    'start_time': datetime.now(),
                    'audio_file': audio_file_path,
                    'status': 'ringing'
                }
                
                # Se c'è un file audio, lo riproduce
                if audio_file_path:
                    time.sleep(2)  # Attende che la chiamata si stabilisca
                    self.pbx.play_audio(phone_extension, audio_file_path)
                
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
