#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per combinare 3 file .ico in un unico file multi-risoluzione
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from PIL import Image
import os

def extract_images_from_ico(ico_path):
    """Estrae tutte le immagini da un file .ico"""
    print(f"  Apertura: {ico_path}")
    img = Image.open(ico_path)
    
    images = []
    try:
        # Alcuni .ico hanno più frame
        for i in range(100):  # Max 100 frame
            img.seek(i)
            # Copia l'immagine corrente
            frame = img.copy()
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            images.append((frame.size, frame))
            print(f"    + {frame.size[0]}x{frame.size[1]}")
    except EOFError:
        pass
    
    return images

def combine_icons():
    """Combina i 3 file .ico in un unico file multi-risoluzione"""
    
    ico_files = [
        "assets/app_icon.ico",
        "assets/app_icon_2.ico",
        "assets/app_icon_3.ico"
    ]
    
    output_ico = "assets/app_icon_combined.ico"
    
    print("="*60)
    print("COMBINAZIONE ICONE MULTI-RISOLUZIONE")
    print("="*60)
    print()
    
    all_images = {}  # Dict: size -> image
    
    # Estrai tutte le immagini da tutti i file
    for ico_file in ico_files:
        if not os.path.exists(ico_file):
            print(f"ATTENZIONE: {ico_file} non trovato, salto...")
            continue
        
        print(f"Estrazione da: {ico_file}")
        images = extract_images_from_ico(ico_file)
        
        # Aggiungi al dizionario (sovrascrive se esiste già quella dimensione)
        for size, img in images:
            all_images[size] = img
        print()
    
    if not all_images:
        print("ERRORE: Nessuna immagine trovata!")
        return False
    
    # Ordina le dimensioni dalla più grande alla più piccola
    sorted_sizes = sorted(all_images.keys(), reverse=True)
    
    print(f"Risoluzioni totali trovate: {len(sorted_sizes)}")
    for size in sorted_sizes:
        print(f"  - {size[0]}x{size[1]}")
    print()
    
    # Prepara la lista di immagini ordinate
    icon_images = [all_images[size] for size in sorted_sizes]
    
    # Salva come .ico multi-risoluzione
    print(f"Salvataggio: {output_ico}")
    icon_images[0].save(
        output_ico,
        format='ICO',
        sizes=sorted_sizes,
        append_images=icon_images[1:]
    )
    
    file_size = os.path.getsize(output_ico)
    print(f"File creato: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # Crea anteprima
    preview_path = "assets/app_icon_combined_preview.png"
    preview = Image.new('RGB', (1024, 256), 'white')
    
    # Mostra le prime 4 risoluzioni
    x_offset = 0
    for i, size in enumerate(sorted_sizes[:4]):
        img = all_images[size]
        # Scala per entrare in 256x256
        if size[0] > 256:
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            display_size = 256
        else:
            display_size = size[0]
        
        # Centra
        y_offset = (256 - display_size) // 2
        x_pos = x_offset + (256 - display_size) // 2
        
        if img.mode == 'RGBA':
            preview.paste(img, (x_pos, y_offset), img)
        else:
            preview.paste(img, (x_pos, y_offset))
        
        x_offset += 256
    
    preview.save(preview_path)
    print(f"Anteprima salvata: {preview_path}")
    
    print()
    print("="*60)
    print("COMPLETATO CON SUCCESSO!")
    print("="*60)
    print()
    print(f"File generato: {output_ico}")
    print(f"Risoluzioni incluse: {len(sorted_sizes)}")
    print()
    print("PROSSIMO PASSO:")
    print("1. Rinomina il file generato in 'app_icon.ico'")
    print("2. Rigenera l'exe con: rebuild_exe.bat")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = combine_icons()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"ERRORE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

