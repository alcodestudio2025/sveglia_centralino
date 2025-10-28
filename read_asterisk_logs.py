#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legge ultimi log Asterisk per debugging snooze"""
import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from config import PBX_CONFIG

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PBX_CONFIG['host'], PBX_CONFIG['port'], 
                PBX_CONFIG['username'], PBX_CONFIG['password'])
    
    print("="*70)
    print("LOG ASTERISK - WAKEUP-SERVICE - ULTIMI 80 RIGHE")
    print("="*70)
    
    # Leggi ultimi log wakeup-service
    cmd = "grep 'wakeup-service' /var/log/asterisk/full 2>/dev/null | tail -80"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='replace')
    
    if output:
        lines = output.strip().split('\n')
        print(f"\nTrovate {len(lines)} righe\n")
        for i, line in enumerate(lines, 1):
            print(f"{i:3}. {line}")
    else:
        print("Nessun log trovato")
    
    ssh.close()
    
except Exception as e:
    print(f"ERRORE: {e}")
    import traceback
    traceback.print_exc()

