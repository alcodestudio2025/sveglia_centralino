#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: verifica accesso file su Asterisk durante chiamata"""
import paramiko
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from config import PBX_CONFIG

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PBX_CONFIG['host'], PBX_CONFIG['port'], 
                PBX_CONFIG['username'], PBX_CONFIG['password'])
    
    print("="*70)
    print("DEBUG FILE ACCESS TEST")
    print("="*70)
    
    # 1. Crea un file di test
    test_id = "130_TEST123"
    test_content = "custom/test_audio"
    
    print(f"\n1. Creazione file di test: /tmp/snooze_5_audio_{test_id}.txt")
    cmd = f"echo -n '{test_content}' > /tmp/snooze_5_audio_{test_id}.txt"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.read()
    print(f"   ✓ File creato")
    
    # 2. Verifica con cat
    print(f"\n2. Lettura con cat:")
    cmd = f"cat /tmp/snooze_5_audio_{test_id}.txt"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    cat_output = stdout.read().decode('utf-8')
    print(f"   Output: [{cat_output}]")
    print(f"   Length: {len(cat_output)}")
    
    # 3. Verifica permessi
    print(f"\n3. Permessi file:")
    cmd = f"ls -la /tmp/snooze_5_audio_{test_id}.txt"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    ls_output = stdout.read().decode('utf-8')
    print(f"   {ls_output.strip()}")
    
    # 4. Verifica owner
    print(f"\n4. Owner file:")
    cmd = f"stat -c '%U %G' /tmp/snooze_5_audio_{test_id}.txt"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stat_output = stdout.read().decode('utf-8')
    print(f"   Owner: {stat_output.strip()}")
    
    # 5. Test Asterisk FILE() function direttamente
    print(f"\n5. Test FILE() function in Asterisk:")
    test_cmd = f"asterisk -rx \"dialplan eval \\${{FILE(/tmp/snooze_5_audio_{test_id}.txt,0,100,l)}}\""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    asterisk_output = stdout.read().decode('utf-8')
    print(f"   Output Asterisk:")
    print(f"   {asterisk_output}")
    
    # 6. Verifica chi esegue Asterisk
    print(f"\n6. Processo Asterisk:")
    cmd = "ps aux | grep asterisk | grep -v grep | head -1"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    ps_output = stdout.read().decode('utf-8')
    print(f"   {ps_output.strip()}")
    
    # 7. Testa accesso da utente asterisk
    print(f"\n7. Test accesso come utente asterisk:")
    cmd = f"sudo -u asterisk cat /tmp/snooze_5_audio_{test_id}.txt 2>&1"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    sudo_output = stdout.read().decode('utf-8')
    sudo_error = stderr.read().decode('utf-8')
    print(f"   Output: [{sudo_output}]")
    if sudo_error:
        print(f"   Error: {sudo_error}")
    
    # Cleanup
    cmd = f"rm -f /tmp/snooze_5_audio_{test_id}.txt"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.read()
    
    ssh.close()
    print("\n" + "="*70)
    
except Exception as e:
    print(f"\nERRORE: {e}")
    import traceback
    traceback.print_exc()

