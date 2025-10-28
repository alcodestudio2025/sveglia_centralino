"""
Gestore delle sveglie e chiamate automatiche
"""
import threading
import time
import logging
from datetime import datetime, timedelta
from database import DatabaseManager
from pbx_connection import PBXManager

class AlarmManager:
    def __init__(self, db_manager=None, pbx_manager=None):
        self.db = db_manager or DatabaseManager()
        self.pbx = pbx_manager or PBXManager()
        self.running = False
        self.alarm_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Configurazione
        self.check_interval = 30  # secondi
        self.call_duration = 60   # secondi per chiamata
        self.max_retries = 3      # tentativi massimi
    
    def start(self):
        """Avvia il gestore delle sveglie"""
        if self.running:
            return
        
        self.running = True
        self.alarm_thread = threading.Thread(target=self._alarm_loop, daemon=True)
        self.alarm_thread.start()
        self.logger.info("Gestore sveglie avviato")
    
    def stop(self):
        """Ferma il gestore delle sveglie"""
        self.running = False
        if self.alarm_thread and self.alarm_thread.is_alive():
            # Timeout ridotto per chiusura rapida (daemon thread)
            self.alarm_thread.join(timeout=0.5)
        self.logger.info("Gestore sveglie fermato")
    
    def _alarm_loop(self):
        """Loop principale per il controllo delle sveglie"""
        while self.running:
            try:
                self._check_pending_alarms()
                self._cleanup_completed_calls()
                
                # Sleep a blocchi per rispondere rapidamente alla chiusura
                for _ in range(int(self.check_interval)):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                self.logger.error(f"Errore nel loop sveglie: {e}")
                # Attesa più lunga in caso di errore, ma interrompibile
                for _ in range(10):
                    if not self.running:
                        break
                    time.sleep(1)
    
    def _check_pending_alarms(self):
        """Controlla le sveglie in attesa"""
        try:
            # Ottiene le sveglie programmate per ora
            now = datetime.now()
            alarms = self.db.get_alarms('scheduled')
            
            for alarm in alarms:
                alarm_time = datetime.fromisoformat(alarm[2])
                
                # Verifica se è il momento della sveglia (con tolleranza di 1 minuto)
                time_diff = abs((alarm_time - now).total_seconds())
                
                if time_diff <= 60:  # Entro 1 minuto
                    self._execute_alarm(alarm)
                    
        except Exception as e:
            self.logger.error(f"Errore nel controllo sveglie: {e}")
    
    def _execute_alarm(self, alarm):
        """Esegue una sveglia specifica con supporto snooze"""
        alarm_id = alarm[0]
        room_number = alarm[1]
        audio_message_id = alarm[3]
        
        try:
            # Ottiene l'interno telefonico della camera
            room_data = self.db.get_room(room_number)
            if not room_data:
                self.logger.error(f"Camera {room_number} non trovata")
                self.db.update_alarm_status(alarm_id, "failed")
                return
            
            # Usa l'interno telefonico se specificato, altrimenti il numero camera
            phone_extension = room_data[2] if len(room_data) > 2 and room_data[2] else room_number
            
            # Ottiene la lingua della camera (colonna 7, dopo phone_extension, description, status, color, label)
            room_language = room_data[7] if len(room_data) > 7 and room_data[7] else 'it'
            
            # Ottiene il file audio principale (wake_up)
            audio_file_path = None
            if audio_message_id:
                audio_messages = self.db.get_audio_messages()
                for msg in audio_messages:
                    if msg[0] == audio_message_id:
                        audio_file_path = msg[2]  # file_path
                        break
            
            # Avvia la chiamata con DTMF per snooze
            success, dtmf_digit = self._execute_alarm_with_snooze(
                phone_extension, 
                audio_file_path,
                alarm_id,
                room_number,
                room_language  # Passa la lingua della camera
            )
            
            if success:
                # Aggiorna lo status della sveglia
                self.db.update_alarm_status(alarm_id, "executing")
                
                # Log della chiamata
                self.db.add_call_log(
                    alarm_id=alarm_id,
                    room_number=room_number,
                    call_time=datetime.now(),
                    status="initiated"
                )
                
                self.logger.info(f"Sveglia eseguita per camera {room_number} (interno {phone_extension})")
                
                # Programma la terminazione della chiamata
                threading.Timer(self.call_duration, self._end_alarm_call, 
                              args=[alarm_id, phone_extension]).start()
            else:
                self.logger.error(f"Errore nell'esecuzione sveglia camera {room_number}: {message}")
                self.db.update_alarm_status(alarm_id, "failed")
                
        except Exception as e:
            self.logger.error(f"Errore nell'esecuzione sveglia: {e}")
            self.db.update_alarm_status(alarm_id, "failed")
    
    def _end_alarm_call(self, alarm_id, phone_extension):
        """Termina una chiamata di sveglia"""
        try:
            # Termina la chiamata
            success, message = self.pbx.end_alarm_call(phone_extension)
            
            if success:
                # Aggiorna lo status
                self.db.update_alarm_status(alarm_id, "completed")
                
                # Log della terminazione
                self.db.add_call_log(
                    alarm_id=alarm_id,
                    room_number="",  # Non abbiamo il numero camera qui
                    call_time=datetime.now(),
                    status="completed"
                )
                
                self.logger.info(f"Chiamata sveglia terminata per interno {phone_extension}")
            else:
                self.logger.error(f"Errore nella terminazione chiamata interno {phone_extension}: {message}")
                
        except Exception as e:
            self.logger.error(f"Errore nella terminazione chiamata: {e}")
    
    def _cleanup_completed_calls(self):
        """Pulisce le chiamate completate"""
        try:
            self.pbx.cleanup_old_calls()
        except Exception as e:
            self.logger.error(f"Errore nella pulizia chiamate: {e}")
    
    def snooze_alarm(self, alarm_id, snooze_minutes):
        """Posticipa una sveglia"""
        try:
            # Ottiene la sveglia
            alarms = self.db.get_alarms()
            alarm = None
            for a in alarms:
                if a[0] == alarm_id:
                    alarm = a
                    break
            
            if not alarm:
                return False, "Sveglia non trovata"
            
            # Calcola la nuova ora
            current_time = datetime.fromisoformat(alarm[2])
            new_time = current_time + timedelta(minutes=snooze_minutes)
            
            # Aggiorna il conteggio rinvii
            current_snooze_count = alarm[5] if len(alarm) > 5 else 0
            new_snooze_count = current_snooze_count + 1
            
            # Crea una nuova sveglia posticipata
            new_alarm_id = self.db.add_alarm(
                room_number=alarm[1],
                alarm_time=new_time.isoformat(),
                audio_message_id=alarm[3]
            )
            
            # Aggiorna lo status della sveglia originale
            self.db.update_alarm_status(alarm_id, "snoozed")
            
            # Log del rinvio
            self.db.add_call_log(
                alarm_id=alarm_id,
                room_number=alarm[1],
                call_time=datetime.now(),
                snooze_minutes=snooze_minutes,
                status="snoozed"
            )
            
            self.logger.info(f"Sveglia {alarm_id} posticipata di {snooze_minutes} minuti")
            return True, f"Sveglia posticipata di {snooze_minutes} minuti"
            
        except Exception as e:
            self.logger.error(f"Errore nel rinvio sveglia: {e}")
            return False, str(e)
    
    def cancel_alarm(self, alarm_id):
        """Cancella una sveglia"""
        try:
            self.db.update_alarm_status(alarm_id, "cancelled")
            
            # Log della cancellazione
            self.db.add_call_log(
                alarm_id=alarm_id,
                room_number="",
                call_time=datetime.now(),
                status="cancelled"
            )
            
            self.logger.info(f"Sveglia {alarm_id} cancellata")
            return True, "Sveglia cancellata"
            
        except Exception as e:
            self.logger.error(f"Errore nella cancellazione sveglia: {e}")
            return False, str(e)
    
    def get_alarm_status(self, alarm_id):
        """Ottiene lo status di una sveglia"""
        try:
            alarms = self.db.get_alarms()
            for alarm in alarms:
                if alarm[0] == alarm_id:
                    return {
                        'id': alarm[0],
                        'room': alarm[1],
                        'time': alarm[2],
                        'status': alarm[4],
                        'snooze_count': alarm[5] if len(alarm) > 5 else 0
                    }
            return None
        except Exception as e:
            self.logger.error(f"Errore nel recupero status sveglia: {e}")
            return None
    
    def get_active_calls(self):
        """Ottiene le chiamate attive"""
        return self.pbx.get_active_calls()
    
    def test_pbx_connection(self):
        """Testa la connessione al centralino"""
        return self.pbx.pbx.test_connection()
    
    def _execute_alarm_with_snooze(self, phone_extension, wake_audio_path, alarm_id, room_number, language='it'):
        """
        Esegue sveglia con opzioni snooze tramite DTMF
        
        Args:
            phone_extension: Interno telefonico
            wake_audio_path: File audio sveglia principale
            alarm_id: ID sveglia nel database
            room_number: Numero camera
            language: Lingua della camera (it, en, etc.)
            
        Returns:
            (success, dtmf_digit): Success e tasto premuto
        """
        try:
            self.logger.info(f"="*60)
            self.logger.info(f"SVEGLIA CON SNOOZE - Camera {room_number} - Interno {phone_extension} - Lingua: {language.upper()}")
            self.logger.info(f"="*60)
            
            # 1. Effettua la chiamata
            command = f"asterisk -rx 'channel originate Local/{phone_extension}@internal extension {phone_extension}@internal'"
            output, error = self.pbx.pbx.execute_command(command)
            
            if error:
                self.logger.error(f"Errore chiamata: {error}")
                return False, None
            
            self.logger.info(f"✓ Chiamata avviata a {phone_extension}")
            time.sleep(3)  # Attende risposta
            
            # 2. Riproduce messaggio principale con opzioni DTMF
            self.logger.info(f"Riproduzione messaggio sveglia con opzioni snooze...")
            success, dtmf_digit = self.pbx.pbx.play_audio_with_dtmf(
                phone_extension,
                wake_audio_path,
                timeout=30
            )
            
            if not success:
                self.logger.error("Errore nella riproduzione audio")
                return False, None
            
            # 3. Gestisce risposta DTMF
            if dtmf_digit == '1':
                # Snooze 5 minuti
                self.logger.info(f"✓ DTMF '1' ricevuto - Snooze 5 minuti")
                snooze_minutes = 5
                confirm_audio = self._get_audio_by_action('snooze_confirm', language, '5')
                
            elif dtmf_digit == '2':
                # Snooze 10 minuti
                self.logger.info(f"✓ DTMF '2' ricevuto - Snooze 10 minuti")
                snooze_minutes = 10
                confirm_audio = self._get_audio_by_action('snooze_confirm', language, '10')
                
            else:
                # Nessun snooze - cliente ha chiuso/non ha premuto nulla
                self.logger.info(f"Nessuno snooze richiesto - Cliente ha chiuso o timeout")
                self.db.update_alarm_status(alarm_id, "completed")
                return True, None
            
            # 4. Riproduce messaggio conferma snooze
            if confirm_audio:
                self.logger.info(f"Riproduzione conferma snooze {snooze_minutes} minuti...")
                self.pbx.pbx.play_audio(phone_extension, confirm_audio)
                time.sleep(2)
            
            # 5. Riprogramma sveglia
            new_alarm_time = datetime.now() + timedelta(minutes=snooze_minutes)
            self.logger.info(f"Riprogrammazione sveglia per {new_alarm_time.strftime('%H:%M')}")
            
            # Aggiorna sveglia esistente
            self.db.update_alarm_status(alarm_id, "snoozed")
            
            # Crea nuova sveglia per snooze
            self.db.add_alarm(
                room_number,
                new_alarm_time.isoformat(),
                audio_message_id=None  # Usa stesso audio della sveglia originale
            )
            
            self.logger.info(f"✓ Sveglia riprogrammata con successo")
            self.logger.info(f"="*60)
            
            return True, dtmf_digit
            
        except Exception as e:
            self.logger.error(f"Errore esecuzione sveglia con snooze: {e}")
            return False, None
    
    def _get_audio_by_action(self, action_type, language='it', variant=None):
        """
        Ottiene file audio per azione specifica
        
        Args:
            action_type: 'wake_up', 'snooze_confirm', 'goodbye'
            language: Codice lingua (it, en, etc.)
            variant: Variante specifica (es. '5min', '10min')
            
        Returns:
            path del file audio o None
        """
        try:
            audio_messages = self.db.get_audio_messages()
            
            for msg in audio_messages:
                # msg = (id, name, file_path, duration, category, language, action_type, created_at)
                msg_action = msg[6] if len(msg) > 6 else None
                msg_language = msg[5] if len(msg) > 5 else 'it'
                msg_name = msg[1]
                
                # Match per action type e lingua
                if msg_action == action_type and msg_language.lower() == language.lower():
                    # Se variant specificato, cerca nel nome
                    if variant:
                        if variant.lower() in msg_name.lower():
                            self.logger.info(f"Audio trovato: {msg_name} ({action_type}, {language}, {variant})")
                            return msg[2]  # file_path
                    else:
                        self.logger.info(f"Audio trovato: {msg_name} ({action_type}, {language})")
                        return msg[2]  # file_path
            
            self.logger.warning(f"Audio non trovato: {action_type}, {language}, {variant}")
            return None
            
        except Exception as e:
            self.logger.error(f"Errore ricerca audio: {e}")
            return None

if __name__ == "__main__":
    # Test del modulo
    alarm_mgr = AlarmManager()
    success, message = alarm_mgr.test_pbx_connection()
    print(f"Test connessione PBX: {success} - {message}")
