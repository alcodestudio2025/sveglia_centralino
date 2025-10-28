"""
Gestione connessione SSH al centralino PBX
"""
import paramiko
import time
import logging
import os
from datetime import datetime
from config import PBX_CONFIG
from logger import get_logger

class PBXConnection:
    def __init__(self, config=None):
        self.config = config or PBX_CONFIG
        self.ssh_client = None
        self.connected = False
        self.last_connection_time = None
        
        # Setup logging
        self.logger = get_logger('pbx_connection')
    
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
        """Effettua una chiamata all'interno telefonico specificato con CallerID personalizzato"""
        try:
            # Ottiene configurazione CallerID per sveglie
            wake_extension = self.config.get('wake_extension', '999')
            wake_callerid = self.config.get('wake_callerid', 'Servizio Sveglie')
            context = self.config.get('context', 'from-internal')
            
            # Comando Asterisk con CallerID come variabile di canale
            # Usa syntax: Local/ext@context/n per no optimization
            command = (
                f"asterisk -rx 'channel originate Local/{phone_extension}@{context}/n "
                f"exten {phone_extension}@{context} "
                f"callerid \"{wake_callerid} <{wake_extension}>\"'"
            )
            
            self.logger.info(f"Chiamata a {phone_extension} come '{wake_callerid} <{wake_extension}>'")
            self.logger.debug(f"Comando: {command}")
            output, error = self.execute_command(command)
            
            if error:
                return False, f"Errore nella chiamata: {error}"
            
            self.logger.info(f"Chiamata effettuata all'interno {phone_extension}")
            return True, "Chiamata effettuata con successo"
            
        except Exception as e:
            self.logger.error(f"Errore nella chiamata all'interno {phone_extension}: {e}")
            return False, str(e)
    
    def play_audio(self, phone_extension, audio_file_path):
        """Riproduce un file audio durante la chiamata"""
        try:
            # Comando per riprodurre audio (da adattare al centralino specifico)
            command = f"asterisk -rx 'playback {audio_file_path}'"
            
            output, error = self.execute_command(command)
            
            if error:
                return False, f"Errore nella riproduzione audio: {error}"
            
            self.logger.info(f"Audio riprodotto per interno {phone_extension}: {audio_file_path}")
            return True, "Audio riprodotto con successo"
            
        except Exception as e:
            self.logger.error(f"Errore nella riproduzione audio: {e}")
            return False, str(e)
    
    def setup_wakeup_context(self):
        """
        Crea/aggiorna il context 'wakeup-service' nel dialplan di Asterisk
        per gestire sveglie con DTMF
        """
        try:
            self.logger.info("Setup context wakeup-service nel dialplan...")
            
            # Context dedicato per sveglie con DTMF
            # NOTA: L'audio viene passato come extension (wakeup-service/<nome_file>)
            context_config = """
[wakeup-service]
; Context per gestione sveglie con DTMF
; Chiamata: Local/130@from-internal extension <nome_file>@wakeup-service
; Il CALL_ID identifica i file temporanei con i path degli audio di conferma

; Extension dinamica: riceve nome file come ${EXTEN}
; Il nome arriva con "-" al posto di "/" (es: custom-wakeup_didimos_asterisk_1)
; Pattern _. matcha QUALSIASI stringa (lettere, numeri, simboli)
exten => _.,1,NoOp(=== SVEGLIA CON SNOOZE ===)
exten => _.,n,NoOp(Audio extension: ${EXTEN})
exten => _.,n,NoOp(Call ID: ${CALL_ID})
exten => _.,n,Answer()
exten => _.,n,Wait(1)
exten => _.,n,Set(TIMEOUT(digit)=5)
exten => _.,n,Set(TIMEOUT(response)=30)
; Riconverti "-" in "/" per path corretto
exten => _.,n,Set(AUDIO_FILE=${STRREPLACE(EXTEN,-,/)})
exten => _.,n,NoOp(Audio file path: ${AUDIO_FILE})
exten => _.,n,Background(${AUDIO_FILE})
exten => _.,n,WaitExten(30)
exten => _.,n,NoOp(Nessun input DTMF - chiusura)
exten => _.,n,Hangup()

; DTMF 1 - Snooze 5 minuti + Riproduce conferma
exten => 1,1,NoOp(DTMF 1 ricevuto - Snooze 5 min)
exten => 1,n,Set(SNOOZE_CHOICE=1)
exten => 1,n,System(echo "1" > /tmp/asterisk_dtmf_${UNIQUEID}.txt)
exten => 1,n,NoOp(File DTMF creato: /tmp/asterisk_dtmf_${UNIQUEID}.txt)
; Leggi path audio conferma dal file temporaneo usando System + FILE
exten => 1,n,Set(AUDIO_FILE_PATH=/tmp/snooze_5_audio_${CALL_ID}.txt)
exten => 1,n,NoOp(Cerco file: ${AUDIO_FILE_PATH})
; Usa FILE() per leggere il contenuto
exten => 1,n,Set(SNOOZE_AUDIO=${FILE(${AUDIO_FILE_PATH},0,1000)})
exten => 1,n,Set(SNOOZE_AUDIO=${STRREPLACE(SNOOZE_AUDIO,\n,)})
exten => 1,n,Set(SNOOZE_AUDIO=${STRREPLACE(SNOOZE_AUDIO,\r,)})
exten => 1,n,NoOp(Audio letto: [${SNOOZE_AUDIO}])
exten => 1,n,GotoIf($["${SNOOZE_AUDIO}" = ""]?noadio)
exten => 1,n,NoOp(Riproduzione conferma: ${SNOOZE_AUDIO})
exten => 1,n,Playback(${SNOOZE_AUDIO})
exten => 1,n,Goto(fine)
exten => 1,n(noadio),NoOp(Nessun audio conferma trovato)
exten => 1,n(fine),Wait(0.5)
exten => 1,n,Hangup()

; DTMF 2 - Snooze 10 minuti + Riproduce conferma
exten => 2,1,NoOp(DTMF 2 ricevuto - Snooze 10 min)
exten => 2,n,Set(SNOOZE_CHOICE=2)
exten => 2,n,System(echo "2" > /tmp/asterisk_dtmf_${UNIQUEID}.txt)
exten => 2,n,NoOp(File DTMF creato: /tmp/asterisk_dtmf_${UNIQUEID}.txt)
; Leggi path audio conferma dal file temporaneo usando System + FILE
exten => 2,n,Set(AUDIO_FILE_PATH=/tmp/snooze_10_audio_${CALL_ID}.txt)
exten => 2,n,NoOp(Cerco file: ${AUDIO_FILE_PATH})
; Usa FILE() per leggere il contenuto
exten => 2,n,Set(SNOOZE_AUDIO=${FILE(${AUDIO_FILE_PATH},0,1000)})
exten => 2,n,Set(SNOOZE_AUDIO=${STRREPLACE(SNOOZE_AUDIO,\n,)})
exten => 2,n,Set(SNOOZE_AUDIO=${STRREPLACE(SNOOZE_AUDIO,\r,)})
exten => 2,n,NoOp(Audio letto: [${SNOOZE_AUDIO}])
exten => 2,n,GotoIf($["${SNOOZE_AUDIO}" = ""]?noadio)
exten => 2,n,NoOp(Riproduzione conferma: ${SNOOZE_AUDIO})
exten => 2,n,Playback(${SNOOZE_AUDIO})
exten => 2,n,Goto(fine)
exten => 2,n(noadio),NoOp(Nessun audio conferma trovato)
exten => 2,n(fine),Wait(0.5)
exten => 2,n,Hangup()

; Timeout o altro input
exten => t,1,NoOp(Timeout - nessun input)
exten => t,n,Hangup()

exten => i,1,NoOp(Input invalido)
exten => i,n,Hangup()
"""
            
            # Path del file di configurazione custom
            config_path = "/etc/asterisk/extensions_custom.conf"
            
            # Crea il file temporaneo locale
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as tmp:
                tmp.write(context_config)
                tmp_path = tmp.name
            
            # Upload via SFTP
            if not self.is_connected():
                if not self.connect():
                    return False, "Impossibile connettersi"
            
            sftp = self.ssh_client.open_sftp()
            sftp.put(tmp_path, config_path)
            sftp.close()
            
            # Rimuovi file temporaneo
            import os
            os.unlink(tmp_path)
            
            # Reload dialplan
            reload_output, reload_error = self.execute_command("asterisk -rx 'dialplan reload'")
            
            if reload_error:
                self.logger.warning(f"Errore reload dialplan: {reload_error}")
            else:
                self.logger.info("✓ Context wakeup-service configurato e caricato")
            
            return True, "Context configurato"
            
        except Exception as e:
            self.logger.error(f"Errore setup context: {e}")
            return False, str(e)
    
    def upload_audio_to_asterisk(self, local_audio_path):
        """
        Carica un file audio sul server Asterisk via SCP
        
        Args:
            local_audio_path: Path locale del file audio
            
        Returns:
            (success, remote_path): Successo e path remoto
        """
        try:
            import os
            
            # Directory standard di Asterisk per audio custom
            remote_dir = "/var/lib/asterisk/sounds/custom/"
            
            # Nome file
            audio_filename = os.path.basename(local_audio_path)
            remote_path = os.path.join(remote_dir, audio_filename)
            
            self.logger.info(f"Upload audio {audio_filename} su Asterisk...")
            
            # Verifica che il file locale esista
            if not os.path.exists(local_audio_path):
                return False, f"File locale non trovato: {local_audio_path}"
            
            # Crea directory custom se non esiste
            mkdir_command = f"mkdir -p {remote_dir}"
            self.execute_command(mkdir_command)
            
            # Upload via SCP usando lo stesso client SSH
            # NOTA: paramiko supporta SCP via sftp
            if not self.is_connected():
                if not self.connect():
                    return False, "Impossibile connettersi al server"
            
            # Usa SFTP per il trasferimento
            sftp = self.ssh_client.open_sftp()
            sftp.put(local_audio_path, remote_path)
            sftp.close()
            
            self.logger.info(f"✓ Audio caricato: {remote_path}")
            
            # Restituisce il nome file senza estensione (per Asterisk)
            audio_name = audio_filename.replace('.wav', '').replace('.mp3', '').replace('.ogg', '')
            return True, f"custom/{audio_name}"
            
        except Exception as e:
            self.logger.error(f"Errore upload audio: {e}")
            return False, str(e)
    
    def play_audio_with_dtmf(self, phone_extension, audio_file_path, snooze_5_audio=None, snooze_10_audio=None, timeout=30):
        """
        Chiama, riproduce audio e attende DTMF usando context wakeup-service
        
        STRATEGIA:
        1. Upload file audio su Asterisk
        2. Upload audio di conferma snooze (se presenti)
        3. Usa context 'wakeup-service' che gestisce DTMF e riproduce conferma
        4. Legge il risultato DTMF dal file temporaneo
        
        Args:
            phone_extension: Interno telefonico
            audio_file_path: File audio da riprodurre
            snooze_5_audio: Path audio conferma 5 minuti (opzionale)
            snooze_10_audio: Path audio conferma 10 minuti (opzionale)
            timeout: Secondi di attesa per input DTMF
            
        Returns:
            (success, dtmf_digit): Tupla con successo e tasto premuto (1, 2, o None)
        """
        try:
            # Ottiene configurazione CallerID
            wake_extension = self.config.get('wake_extension', '999')
            wake_callerid = self.config.get('wake_callerid', 'Servizio Sveglie')
            context = self.config.get('context', 'from-internal')
            
            # 1. Upload audio sveglia su Asterisk
            self.logger.info(f"Upload audio sveglia: {audio_file_path}")
            success, audio_path_or_error = self.upload_audio_to_asterisk(audio_file_path)
            
            if not success:
                self.logger.error(f"Errore upload: {audio_path_or_error}")
                return False, None
            
            audio_name = audio_path_or_error  # Es: "custom/wakeup_didimos_asterisk_1"
            
            # 2. Upload audio conferma snooze (se presenti)
            snooze_5_path = ""
            snooze_10_path = ""
            
            if snooze_5_audio:
                self.logger.info(f"Upload audio conferma 5min: {snooze_5_audio}")
                success_5, path_5 = self.upload_audio_to_asterisk(snooze_5_audio)
                if success_5:
                    snooze_5_path = path_5
                    self.logger.info(f"✓ Conferma 5min: {snooze_5_path}")
            
            if snooze_10_audio:
                self.logger.info(f"Upload audio conferma 10min: {snooze_10_audio}")
                success_10, path_10 = self.upload_audio_to_asterisk(snooze_10_audio)
                if success_10:
                    snooze_10_path = path_10
                    self.logger.info(f"✓ Conferma 10min: {snooze_10_path}")
            
            # 3. Genera un ID univoco per questa chiamata
            import time
            call_id = f"{phone_extension}_{int(time.time())}"
            
            # 4. Scrivi i path degli audio in file temporanei per il dialplan
            # Il dialplan leggerà questi file per sapere quali audio riprodurre
            # NOTA: Usa echo -n per evitare newline finale
            if snooze_5_path or snooze_10_path:
                # Crea file temporanei sul server Asterisk
                if snooze_5_path:
                    cmd_5 = f"echo -n '{snooze_5_path}' > /tmp/snooze_5_audio_{call_id}.txt"
                    output_5, error_5 = self.execute_command(cmd_5)
                    self.logger.info(f"✓ File snooze 5min creato: /tmp/snooze_5_audio_{call_id}.txt")
                    self.logger.info(f"  Contenuto: {snooze_5_path}")
                    
                    # Verifica che il file esista
                    verify_cmd = f"cat /tmp/snooze_5_audio_{call_id}.txt"
                    verify_out, _ = self.execute_command(verify_cmd)
                    self.logger.info(f"  Verifica contenuto: [{verify_out}]")
                
                if snooze_10_path:
                    cmd_10 = f"echo -n '{snooze_10_path}' > /tmp/snooze_10_audio_{call_id}.txt"
                    output_10, error_10 = self.execute_command(cmd_10)
                    self.logger.info(f"✓ File snooze 10min creato: /tmp/snooze_10_audio_{call_id}.txt")
                    self.logger.info(f"  Contenuto: {snooze_10_path}")
                    
                    # Verifica che il file esista
                    verify_cmd = f"cat /tmp/snooze_10_audio_{call_id}.txt"
                    verify_out, _ = self.execute_command(verify_cmd)
                    self.logger.info(f"  Verifica contenuto: [{verify_out}]")
            
            # 5. Comando Originate verso il context wakeup-service
            # Passa il nome file direttamente come extension
            # Passa anche il call_id per identificare i file temporanei
            # NOTA: Sostituiamo "/" con "-" per compatibilità extension pattern
            audio_exten = audio_name.replace('/', '-')
            
            command = (
                f"asterisk -rx \"channel originate Local/{phone_extension}@{context}/n "
                f"extension {audio_exten}@wakeup-service "
                f"callerid '{wake_callerid} <{wake_extension}>' "
                f"variable CALL_ID={call_id}\" "
            )
            
            self.logger.info(f"Chiamata con DTMF a {phone_extension}: {audio_name}")
            self.logger.debug(f"Comando: {command}")
            
            output, error = self.execute_command(command)
            
            if error:
                self.logger.error(f"Errore comando: {error}")
                return False, None
            
            self.logger.info(f"✓ Chiamata avviata verso wakeup-service")
            
            # 4. Aspetta che la chiamata finisca e leggi il risultato DTMF
            # Il context scrive il digit in /tmp/asterisk_dtmf_*.txt
            import time
            time.sleep(timeout + 5)  # Attende che la chiamata finisca
            
            # 5. Cerca il file DTMF
            # Pattern: /tmp/asterisk_dtmf_*
            list_cmd = "ls -t /tmp/asterisk_dtmf_* 2>/dev/null | head -1"
            dtmf_file_output, _ = self.execute_command(list_cmd)
            
            if dtmf_file_output and dtmf_file_output.strip():
                dtmf_file = dtmf_file_output.strip()
                
                # Leggi il contenuto
                read_cmd = f"cat {dtmf_file}"
                dtmf_content, _ = self.execute_command(read_cmd)
                
                if dtmf_content:
                    dtmf_digit = dtmf_content.strip()
                    self.logger.info(f"✓ DTMF ricevuto: {dtmf_digit}")
                    
                    # Pulisci i file temporanei
                    self.execute_command(f"rm -f {dtmf_file}")
                    self.execute_command(f"rm -f /tmp/snooze_5_audio_{call_id}.txt")
                    self.execute_command(f"rm -f /tmp/snooze_10_audio_{call_id}.txt")
                    
                    return True, dtmf_digit if dtmf_digit in ['1', '2'] else None
            
            self.logger.info("Nessun DTMF ricevuto (timeout o no input)")
            # Pulisci comunque i file temporanei
            self.execute_command(f"rm -f /tmp/snooze_5_audio_{call_id}.txt")
            self.execute_command(f"rm -f /tmp/snooze_10_audio_{call_id}.txt")
            return True, None
            
        except Exception as e:
            self.logger.error(f"Errore riproduzione audio con DTMF: {e}")
            # Pulisci i file temporanei anche in caso di errore
            try:
                self.execute_command(f"rm -f /tmp/snooze_5_audio_{call_id}.txt")
                self.execute_command(f"rm -f /tmp/snooze_10_audio_{call_id}.txt")
            except:
                pass
            return False, None
    
    def play_audio_simple(self, phone_extension, audio_file_path):
        """
        Riproduce un audio senza attendere DTMF (per messaggi di conferma)
        
        Args:
            phone_extension: Interno da chiamare
            audio_file_path: Path locale del file audio
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Upload audio su Asterisk
            audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
            
            self.logger.info(f"Upload audio conferma su Asterisk: {audio_file_path}")
            success = self.upload_audio_to_asterisk(audio_file_path)
            if not success:
                return False, "Errore upload audio"
            
            # Prepara path audio per Asterisk (senza estensione)
            asterisk_audio_path = f"custom/{audio_filename}"
            
            # Converti "/" in "-" per extension name
            audio_exten = asterisk_audio_path.replace('/', '-')
            
            # Usa wakeup-service-simple context (senza DTMF)
            context = self.config.get('context', 'from-internal')
            wake_extension = self.config.get('wake_extension', '999')
            wake_callerid = self.config.get('wake_callerid', 'Servizio Sveglie')
            
            self.logger.info(f"Riproduzione audio semplice a {phone_extension}: {asterisk_audio_path}")
            
            # Chiamata SENZA DTMF usando context dedicato
            command = (
                f"asterisk -rx \"channel originate Local/{phone_extension}@{context}/n "
                f"extension {audio_exten}@wakeup-service-simple "
                f"callerid '{wake_callerid} <{wake_extension}>'\" "
            )
            
            output, error = self.execute_command(command)
            
            if error or "error" in output.lower():
                self.logger.error(f"Errore chiamata: {output}")
                return False, "Errore chiamata"
            
            self.logger.info(f"✓ Audio semplice riprodotto")
            return True, "Audio riprodotto"
            
        except Exception as e:
            self.logger.error(f"Errore riproduzione audio semplice: {e}")
            return False, str(e)
    
    def _extract_dtmf_from_output(self, output):
        """Estrae il digit DTMF dall'output del comando Asterisk"""
        import re
        
        # Pattern per cercare digit DTMF nell'output
        patterns = [
            r'DTMF[:\s]+([0-9#*])',
            r'digit[:\s]+([0-9#*])',
            r'pressed[:\s]+([0-9#*])',
            r'input[:\s]+([0-9#*])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
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
        self.logger.info("Prime 5 righe output SIP:")
        for i, line in enumerate(lines[:5]):
            self.logger.info(f"  Riga {i}: {line[:80]}")
        
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
                    elif 'UNKNOWN' in line or 'Unspecified' in line or '(unspecified)' in line:
                        status = 'offline'
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
                    
                    peer_data = {
                        'extension': peer_name,
                        'status': status,
                        'latency': latency,
                        'type': 'SIP'
                    }
                    peers.append(peer_data)
                    
                    # Log solo primi 3 per non spammare
                    if len(peers) <= 3:
                        self.logger.info(f"  Parsed: {peer_name} -> {status} (latency: {latency}ms)")
        
        # Summary dettagliato
        online_count = sum(1 for p in peers if p['status'] == 'online')
        offline_count = sum(1 for p in peers if p['status'] == 'offline')
        unmonitored_count = sum(1 for p in peers if p['status'] == 'unmonitored')
        
        self.logger.info(f"Trovati {len(peers)} interni SIP: {online_count} online, {offline_count} offline, {unmonitored_count} unmonitored")
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
