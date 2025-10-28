#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per ottimizzare l'icona creando tutte le risoluzioni standard per Windows
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from PIL import Image
import os

def optimize_icon():
    """Crea un'icona con tutte le risoluzioni standard Windows"""
    
    # Usa la versione più grande come sorgente
    source_ico = "assets/app_icon.ico"
    output_ico = "assets/app_icon_final.ico"
    
    print("="*60)
    print("OTTIMIZZAZIONE ICONA PER WINDOWS")
    print("="*60)
    print()
    
    print(f"Caricamento: {source_ico}")
    img = Image.open(source_ico)
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    print(f"Dimensione originale: {img.size[0]}x{img.size[1]}")
    print()
    
    # Risoluzioni standard per Windows (ordinate dalla più grande)
    standard_sizes = [
        (256, 256),  # Icone molto grandi
        (128, 128),  # Icone grandi
        (96, 96),    # Icone grandi (alta DPI)
        (64, 64),    # Icone medie
        (48, 48),    # Icone normali
        (32, 32),    # Icone piccole
        (24, 24),    # Icone piccole (alta DPI)
        (16, 16),    # Icone minime
    ]
    
    print(f"Creazione di {len(standard_sizes)} risoluzioni standard:")
    
    icon_images = []
    for size in standard_sizes:
        # Ridimensiona con antialiasing di alta qualità
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icon_images.append(resized)
        print(f"  + {size[0]}x{size[1]}")
    
    print()
    print(f"Salvataggio: {output_ico}")
    
    # Salva come .ico multi-risoluzione
    icon_images[0].save(
        output_ico,
        format='ICO',
        sizes=standard_sizes,
        append_images=icon_images[1:]
    )
    
    file_size = os.path.getsize(output_ico)
    print(f"File creato: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # Backup dell'icona vecchia
    backup_path = "assets/app_icon_old.ico"
    if os.path.exists("assets/app_icon.ico"):
        import shutil
        shutil.copy2("assets/app_icon.ico", backup_path)
        print(f"Backup salvato: {backup_path}")
    
    # Sostituisci l'icona principale
    import shutil
    shutil.copy2(output_ico, "assets/app_icon.ico")
    print(f"Icona principale aggiornata: assets/app_icon.ico")
    
    # Crea anteprima
    preview_path = "assets/app_icon_preview.png"
    preview = Image.new('RGB', (1024, 256), 'white')
    
    # Mostra 4 risoluzioni diverse
    preview_sizes = [(256, 256), (128, 128), (64, 64), (32, 32)]
    x_offset = 0
    for size in preview_sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        # Centra
        y_offset = (256 - size[1]) // 2
        x_pos = x_offset + (256 - size[0]) // 2
        
        if resized.mode == 'RGBA':
            preview.paste(resized, (x_pos, y_offset), resized)
        else:
            preview.paste(resized, (x_pos, y_offset))
        
        x_offset += 256
    
    preview.save(preview_path)
    print(f"Anteprima salvata: {preview_path}")
    
    print()
    print("="*60)
    print("OTTIMIZZAZIONE COMPLETATA!")
    print("="*60)
    print()
    print(f"Icona ottimizzata: assets/app_icon.ico")
    print(f"Risoluzioni: {len(standard_sizes)} (da 256x256 a 16x16)")
    print()
    print("L'icona sara' ora nitida a TUTTE le dimensioni!")
    print()
    print("PROSSIMO PASSO: Rigenera l'exe con rebuild_exe.bat")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = optimize_icon()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"ERRORE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

