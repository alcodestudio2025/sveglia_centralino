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
        if self.alarm_thread:
            self.alarm_thread.join(timeout=5)
        self.logger.info("Gestore sveglie fermato")
    
    def _alarm_loop(self):
        """Loop principale per il controllo delle sveglie"""
        while self.running:
            try:
                self._check_pending_alarms()
                self._cleanup_completed_calls()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Errore nel loop sveglie: {e}")
                time.sleep(10)  # Attesa più lunga in caso di errore
    
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
        """Esegue una sveglia specifica"""
        alarm_id = alarm[0]
        room_number = alarm[1]
        audio_message_id = alarm[3]
        
        try:
            # Ottiene il file audio se specificato
            audio_file_path = None
            if audio_message_id:
                audio_messages = self.db.get_audio_messages()
                for msg in audio_messages:
                    if msg[0] == audio_message_id:
                        audio_file_path = msg[2]  # file_path
                        break
            
            # Avvia la chiamata
            success, message = self.pbx.start_alarm_call(room_number, audio_file_path)
            
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
                
                self.logger.info(f"Sveglia eseguita per camera {room_number}")
                
                # Programma la terminazione della chiamata
                threading.Timer(self.call_duration, self._end_alarm_call, 
                              args=[alarm_id, room_number]).start()
            else:
                self.logger.error(f"Errore nell'esecuzione sveglia camera {room_number}: {message}")
                self.db.update_alarm_status(alarm_id, "failed")
                
        except Exception as e:
            self.logger.error(f"Errore nell'esecuzione sveglia: {e}")
            self.db.update_alarm_status(alarm_id, "failed")
    
    def _end_alarm_call(self, alarm_id, room_number):
        """Termina una chiamata di sveglia"""
        try:
            # Termina la chiamata
            success, message = self.pbx.end_alarm_call(room_number)
            
            if success:
                # Aggiorna lo status
                self.db.update_alarm_status(alarm_id, "completed")
                
                # Log della terminazione
                self.db.add_call_log(
                    alarm_id=alarm_id,
                    room_number=room_number,
                    call_time=datetime.now(),
                    status="completed"
                )
                
                self.logger.info(f"Chiamata sveglia terminata per camera {room_number}")
            else:
                self.logger.error(f"Errore nella terminazione chiamata camera {room_number}: {message}")
                
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

if __name__ == "__main__":
    # Test del modulo
    alarm_mgr = AlarmManager()
    success, message = alarm_mgr.test_pbx_connection()
    print(f"Test connessione PBX: {success} - {message}")
