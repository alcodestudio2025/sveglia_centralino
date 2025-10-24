"""
Sistema di logging per il sistema di gestione sveglie
"""
import logging
import os
import datetime
from logging.handlers import RotatingFileHandler
from config import create_directories

class SystemLogger:
    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
        self.setup_logging()
    
    def setup_logging(self):
        """Configura il sistema di logging"""
        # Crea la cartella logs se non esiste
        create_directories()
        
        # Configurazione del logger principale
        self.logger = logging.getLogger('sveglia_centralino')
        self.logger.setLevel(self.log_level)
        
        # Rimuove handler esistenti per evitare duplicati
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler per file di log con rotazione
        log_file = os.path.join('logs', 'sveglia_centralino.log')
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # Handler per console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Aggiunge gli handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Logger specifici per moduli
        self.setup_module_loggers()
    
    def setup_module_loggers(self):
        """Configura logger specifici per i moduli"""
        modules = ['pbx_connection', 'alarm_manager', 'database', 'main']
        
        for module in modules:
            module_logger = logging.getLogger(f'sveglia_centralino.{module}')
            module_logger.setLevel(self.log_level)
    
    def get_logger(self, module_name=None):
        """Ottiene un logger per un modulo specifico"""
        if module_name:
            return logging.getLogger(f'sveglia_centralino.{module_name}')
        return self.logger
    
    def log_alarm_event(self, event_type, room_number, message, details=None):
        """Log specifico per eventi sveglie"""
        log_data = {
            'event_type': event_type,
            'room_number': room_number,
            'message': message,
            'timestamp': datetime.datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(f"ALARM_EVENT: {log_data}")
    
    def log_pbx_event(self, event_type, command, result, error=None):
        """Log specifico per eventi PBX"""
        log_data = {
            'event_type': event_type,
            'command': command,
            'result': result,
            'timestamp': datetime.datetime.now().isoformat(),
            'error': error
        }
        
        if error:
            self.logger.error(f"PBX_EVENT: {log_data}")
        else:
            self.logger.info(f"PBX_EVENT: {log_data}")
    
    def log_system_event(self, event_type, component, message, level='INFO'):
        """Log specifico per eventi sistema"""
        log_data = {
            'event_type': event_type,
            'component': component,
            'message': message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if level == 'ERROR':
            self.logger.error(f"SYSTEM_EVENT: {log_data}")
        elif level == 'WARNING':
            self.logger.warning(f"SYSTEM_EVENT: {log_data}")
        else:
            self.logger.info(f"SYSTEM_EVENT: {log_data}")
    
    def get_log_files(self):
        """Ottiene la lista dei file di log"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            return []
        
        log_files = []
        for file in os.listdir(log_dir):
            if file.endswith('.log'):
                file_path = os.path.join(log_dir, file)
                stat = os.stat(file_path)
                log_files.append({
                    'name': file,
                    'path': file_path,
                    'size': stat.st_size,
                    'modified': datetime.datetime.fromtimestamp(stat.st_mtime)
                })
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    
    def clear_old_logs(self, days=30):
        """Pulisce i log più vecchi di N giorni"""
        log_files = self.get_log_files()
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        deleted_count = 0
        for log_file in log_files:
            if log_file['modified'] < cutoff_date:
                try:
                    os.remove(log_file['path'])
                    deleted_count += 1
                    self.logger.info(f"Log file eliminato: {log_file['name']}")
                except Exception as e:
                    self.logger.error(f"Errore nell'eliminazione log {log_file['name']}: {e}")
        
        return deleted_count
    
    def export_logs(self, output_file, start_date=None, end_date=None, level=None):
        """Esporta i log in un file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Log Export - Sistema Gestione Sveglie Hotel\n")
                f.write(f"# Esportato il: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# " + "="*50 + "\n\n")
                
                # Legge i log dal file principale
                log_file = os.path.join('logs', 'sveglia_centralino.log')
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as log_f:
                        for line in log_f:
                            # Filtra per data se specificata
                            if start_date or end_date:
                                try:
                                    log_time = datetime.datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
                                    if start_date and log_time < start_date:
                                        continue
                                    if end_date and log_time > end_date:
                                        continue
                                except:
                                    pass
                            
                            # Filtra per livello se specificato
                            if level and level.upper() not in line:
                                continue
                            
                            f.write(line)
            
            self.logger.info(f"Log esportati in: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Errore nell'esportazione log: {e}")
            return False

# Istanza globale del logger
system_logger = SystemLogger()

def get_logger(module_name=None):
    """Funzione helper per ottenere un logger"""
    return system_logger.get_logger(module_name)

if __name__ == "__main__":
    # Test del sistema di logging
    logger = get_logger('test')
    logger.info("Test del sistema di logging")
    logger.error("Test errore")
    
    # Test funzioni specifiche
    system_logger.log_alarm_event('test', '101', 'Test sveglia')
    system_logger.log_pbx_event('test', 'test_command', 'success')
    system_logger.log_system_event('test', 'main', 'Test sistema')
    
    print("Sistema di logging testato con successo")
