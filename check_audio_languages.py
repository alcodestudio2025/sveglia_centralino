#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica configurazione audio per lingue"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from database import DatabaseManager

db = DatabaseManager()

print("="*70)
print("VERIFICA AUDIO MESSAGGI - TUTTE LE LINGUE")
print("="*70)

audio_messages = db.get_audio_messages()

print(f"\nTotale audio: {len(audio_messages)}\n")

# Raggruppa per lingua
by_language = {}
by_action = {}

for msg in audio_messages:
    # msg = (id, name, file_path, duration, category, language, action_type, created_at)
    msg_id = msg[0]
    msg_name = msg[1]
    msg_path = msg[2]
    msg_language = msg[5] if len(msg) > 5 else 'N/A'
    msg_action = msg[6] if len(msg) > 6 else 'N/A'
    
    if msg_language not in by_language:
        by_language[msg_language] = []
    by_language[msg_language].append(msg)
    
    key = f"{msg_action}_{msg_language}"
    if key not in by_action:
        by_action[key] = []
    by_action[key].append(msg)

print("AUDIO PER LINGUA:")
print("-" * 70)
for lang, msgs in sorted(by_language.items()):
    print(f"\n{lang.upper()} ({len(msgs)} audio):")
    for msg in msgs:
        msg_id = msg[0]
        msg_name = msg[1]
        msg_action = msg[6] if len(msg) > 6 else 'N/A'
        print(f"  [{msg_id}] {msg_name} (action: {msg_action})")

print("\n" + "="*70)
print("AUDIO PER ACTION + LINGUA:")
print("-" * 70)

for action_lang, msgs in sorted(by_action.items()):
    action, lang = action_lang.rsplit('_', 1)
    print(f"\n{action} - {lang.upper()}:")
    for msg in msgs:
        msg_id = msg[0]
        msg_name = msg[1]
        print(f"  [{msg_id}] {msg_name}")

print("\n" + "="*70)
print("VERIFICA SNOOZE_CONFIRM:")
print("-" * 70)

snooze_confirms = [msg for msg in audio_messages if (len(msg) > 6 and msg[6] == 'snooze_confirm')]
print(f"\nTotale snooze_confirm: {len(snooze_confirms)}\n")

for msg in snooze_confirms:
    msg_id = msg[0]
    msg_name = msg[1]
    msg_path = msg[2]
    msg_language = msg[5] if len(msg) > 5 else 'N/A'
    
    has_5 = '5' in msg_name.lower()
    has_10 = '10' in msg_name.lower()
    
    print(f"[{msg_id}] {msg_name}")
    print(f"     Lingua: {msg_language}")
    print(f"     Path: {msg_path}")
    print(f"     Contiene '5': {has_5}")
    print(f"     Contiene '10': {has_10}")
    print()

print("="*70)

