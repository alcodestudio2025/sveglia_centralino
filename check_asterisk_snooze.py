#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script diagnostico per verificare il funzionamento dello snooze su Asterisk
"""
import paramiko
import sys
import io

# Fix encoding per Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from config import PBX_CONFIG

def check_asterisk_setup():
    """Verifica setup Asterisk per snooze"""
    
    print("="*70)
    print("DIAGNOSTICA SNOOZE ASTERISK")
    print("="*70)
    
    try:
        # Connessione SSH
        print(f"\n1. Connessione a {PBX_CONFIG['host']}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=PBX_CONFIG['host'],
            port=PBX_CONFIG['port'],
            username=PBX_CONFIG['username'],
            password=PBX_CONFIG['password'],
            timeout=10
        )
        print("   ✓ Connesso")
        
        # Verifica context wakeup-service
        print("\n2. Verifica context wakeup-service nel dialplan...")
        stdin, stdout, stderr = ssh.exec_command("asterisk -rx 'dialplan show wakeup-service'")
        output = stdout.read().decode('utf-8')
        if 'wakeup-service' in output:
            print("   ✓ Context trovato")
            # Conta le extension
            extensions = output.count("exten =>")
            print(f"   ✓ Extension trovate: {extensions}")
        else:
            print("   ✗ Context NON trovato!")
            return False
        
        # Verifica file audio custom
        print("\n3. Verifica file audio in /var/lib/asterisk/sounds/custom/...")
        stdin, stdout, stderr = ssh.exec_command("ls -lh /var/lib/asterisk/sounds/custom/*.wav 2>/dev/null")
        output = stdout.read().decode('utf-8')
        if output:
            files = output.strip().split('\n')
            print(f"   ✓ File audio trovati: {len(files)}")
            for f in files[:5]:  # Mostra primi 5
                print(f"     - {f.split()[-1]}")
        else:
            print("   ⚠ Nessun file audio trovato")
        
        # Verifica file temporanei recenti
        print("\n4. Verifica file temporanei recenti...")
        stdin, stdout, stderr = ssh.exec_command("ls -lht /tmp/snooze_* /tmp/asterisk_dtmf_* 2>/dev/null | head -10")
        output = stdout.read().decode('utf-8')
        if output:
            print("   ⚠ File temporanei ancora presenti (dovrebbero essere puliti):")
            for line in output.strip().split('\n'):
                print(f"     {line}")
        else:
            print("   ✓ Nessun file temporaneo (corretto - sono stati puliti)")
        
        # Verifica ultimi log Asterisk con wakeup-service
        print("\n5. Ultimi log Asterisk con 'wakeup-service'...")
        stdin, stdout, stderr = ssh.exec_command(
            "grep 'wakeup-service' /var/log/asterisk/full 2>/dev/null | tail -20"
        )
        output = stdout.read().decode('utf-8')
        if output:
            lines = output.strip().split('\n')
            print(f"   ✓ Trovate {len(lines)} righe di log recenti")
            print("\n   Ultime 10 righe:")
            for line in lines[-10:]:
                # Mostra solo la parte dopo il timestamp
                if '] ' in line:
                    log_msg = line.split('] ', 1)[1] if len(line.split('] ', 1)) > 1 else line
                    print(f"     {log_msg[:100]}")
        else:
            print("   ✗ Nessun log trovato con 'wakeup-service'")
        
        # Verifica SHELL() function support
        print("\n6. Verifica supporto SHELL() in Asterisk...")
        stdin, stdout, stderr = ssh.exec_command("asterisk -rx 'core show function SHELL'")
        output = stdout.read().decode('utf-8')
        if 'SHELL' in output and 'not found' not in output.lower():
            print("   ✓ SHELL() function supportata")
            if 'enabled' in output.lower():
                print("   ✓ SHELL() abilitata")
            else:
                print("   ⚠ SHELL() potrebbe non essere abilitata")
                print("     Controlla /etc/asterisk/asterisk.conf")
        else:
            print("   ✗ SHELL() function NON supportata!")
            print("     SOLUZIONE: Usa System() invece di SHELL()")
        
        # Verifica extensions_custom.conf
        print("\n7. Verifica extensions_custom.conf...")
        stdin, stdout, stderr = ssh.exec_command("wc -l /etc/asterisk/extensions_custom.conf 2>/dev/null")
        output = stdout.read().decode('utf-8')
        if output and output.strip():
            lines = output.split()[0]
            print(f"   ✓ File presente ({lines} righe)")
            
            # Mostra le prime righe del context wakeup-service
            stdin, stdout, stderr = ssh.exec_command(
                "grep -A 30 '\\[wakeup-service\\]' /etc/asterisk/extensions_custom.conf 2>/dev/null"
            )
            output = stdout.read().decode('utf-8')
            if output:
                print("\n   Prime righe del context:")
                for i, line in enumerate(output.strip().split('\n')[:15]):
                    print(f"     {line}")
        else:
            print("   ✗ File NON trovato!")
        
        # Test manuale SHELL
        print("\n8. Test manuale lettura file con cat...")
        # Crea un file di test
        test_content = "custom/test_audio"
        stdin, stdout, stderr = ssh.exec_command(f"echo -n '{test_content}' > /tmp/test_snooze.txt")
        stdout.read()
        
        # Leggi con cat (come fa il dialplan)
        stdin, stdout, stderr = ssh.exec_command("cat /tmp/test_snooze.txt 2>/dev/null")
        output = stdout.read().decode('utf-8')
        if output.strip() == test_content:
            print(f"   ✓ cat funziona correttamente: [{output.strip()}]")
        else:
            print(f"   ✗ cat non funziona: atteso [{test_content}], ricevuto [{output.strip()}]")
        
        # Pulizia
        stdin, stdout, stderr = ssh.exec_command("rm -f /tmp/test_snooze.txt")
        stdout.read()
        
        ssh.close()
        
        print("\n" + "="*70)
        print("DIAGNOSTICA COMPLETATA")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_asterisk_setup()
    sys.exit(0 if success else 1)

