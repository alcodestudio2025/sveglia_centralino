"""
Test diagnostico per chiamate Asterisk
"""
from pbx_connection import PBXConnection
from config import PBX_CONFIG
from logger import get_logger

logger = get_logger('test_diagnostics')

def test_diagnostics():
    """Esegue una serie di test diagnostici"""
    pbx = PBXConnection()
    
    print("="*60)
    print("TEST DIAGNOSTICI CHIAMATA ASTERISK")
    print("="*60)
    
    # Test 1: Verifica stato interno
    print("\n[1] VERIFICA STATO INTERNO 130")
    print("-"*60)
    
    command = "asterisk -rx 'sip show peer 130'"
    output, error = pbx.execute_command(command)
    
    if output:
        print(f"OK - Output:\n{output}")
    else:
        print(f"ERRORE: {error}")
        print("\nProvo con PJSIP...")
        command = "asterisk -rx 'pjsip show endpoint 130'"
        output, error = pbx.execute_command(command)
        if output:
            print(f"OK - Output PJSIP:\n{output}")
    
    # Test 2: Verifica canali attivi
    print("\n[2] VERIFICA CANALI ATTIVI")
    print("-"*60)
    
    command = "asterisk -rx 'core show channels'"
    output, error = pbx.execute_command(command)
    
    if output:
        print(f"OK - Canali attivi:\n{output}")
    else:
        print(f"ERRORE: {error}")
    
    # Test 3: Verifica dialplan per context internal
    print("\n[3] VERIFICA DIALPLAN - CONTEXT INTERNAL")
    print("-"*60)
    
    command = "asterisk -rx 'dialplan show internal'"
    output, error = pbx.execute_command(command)
    
    if output:
        print(f"OK - Dialplan internal:\n{output[:500]}...")  # Prime 500 righe
    else:
        print(f"ERRORE: {error}")
    
    # Test 4: Test chiamata con verbose output
    print("\n[4] TEST CHIAMATA CON OUTPUT VERBOSO")
    print("-"*60)
    print("ATTENZIONE: Questo fara' squillare il telefono 130!")
    input("Premi INVIO per procedere con il test...")
    
    command = "asterisk -rx 'channel originate Local/130@internal extension 130@internal'"
    print(f"\nChiamata - Eseguo comando: {command}")
    
    output, error = pbx.execute_command(command)
    
    if error:
        print(f"ERRORE nella chiamata:\n{error}")
    else:
        print(f"OK - Chiamata avviata!")
        print(f"Output:\n{output}")
    
    # Controlla lo stato dopo 3 secondi
    import time
    print("\nAttendo 3 secondi...")
    time.sleep(3)
    
    command = "asterisk -rx 'core show channels'"
    output, error = pbx.execute_command(command)
    print(f"\nCanali dopo chiamata:\n{output}")
    
    # Test 5: Verifica log Asterisk
    print("\n[5] ULTIMI LOG ASTERISK")
    print("-"*60)
    
    command = "asterisk -rx 'core show verbose 5'"
    output, error = pbx.execute_command(command)
    
    if output:
        print(f"OK - Log Asterisk attivato")
    
    print("\n="*60)
    print("TEST COMPLETATI")
    print("="*60)
    
    pbx.disconnect()

if __name__ == "__main__":
    test_diagnostics()

