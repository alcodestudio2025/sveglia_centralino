#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per creare un'icona .ico multi-risoluzione ottimizzata per Windows
a partire da icona_3.png
"""

from PIL import Image
import os

def create_multisize_icon():
    """Crea un file .ico con tutte le risoluzioni necessarie per Windows"""
    
    # Percorsi
    source_png = "assets/icona_3.png"
    output_ico = "assets/app_icon.ico"
    
    print(f"📂 Caricamento immagine sorgente: {source_png}")
    
    try:
        # Carica l'immagine PNG originale
        img = Image.open(source_png)
        
        # Converti in RGBA se necessario
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        print(f"✓ Immagine caricata: {img.size[0]}x{img.size[1]} pixels")
        
        # Definisci tutte le risoluzioni necessarie per Windows
        # Queste coprono tutte le visualizzazioni da "icone molto grandi" a "icone piccole"
        sizes = [
            (256, 256),  # Icone molto grandi, Windows 10/11
            (128, 128),  # Icone grandi
            (96, 96),    # Icone medie/grandi (96 DPI)
            (72, 72),    # Icone medie
            (64, 64),    # Icone medie (standard)
            (48, 48),    # Icone normali/liste
            (40, 40),    # Icone normali (125% DPI)
            (32, 32),    # Icone piccole
            (24, 24),    # Icone molto piccole (125% DPI)
            (20, 20),    # Icone molto piccole
            (16, 16),    # Icone minime (taskbar, ecc.)
        ]
        
        print(f"🔧 Creazione di {len(sizes)} risoluzioni...")
        
        # Crea una lista di immagini ridimensionate con antialiasing di alta qualità
        icon_images = []
        for size in sizes:
            # Usa LANCZOS per il miglior antialiasing
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
            print(f"  ✓ {size[0]}x{size[1]}")
        
        # Salva come .ico multi-risoluzione
        print(f"💾 Salvataggio: {output_ico}")
        icon_images[0].save(
            output_ico,
            format='ICO',
            sizes=sizes,
            append_images=icon_images[1:]
        )
        
        # Verifica dimensione file
        file_size = os.path.getsize(output_ico)
        print(f"✓ File creato: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Crea anche un'anteprima
        preview_path = "assets/app_icon_preview.png"
        preview = Image.new('RGB', (768, 256), 'white')
        
        # Mostra 3 diverse risoluzioni nell'anteprima
        preview_sizes = [(256, 256), (128, 128), (64, 64)]
        x_offset = 0
        for i, size in enumerate(preview_sizes):
            resized = img.resize(size, Image.Resampling.LANCZOS)
            # Centra verticalmente
            y_offset = (256 - size[1]) // 2
            if resized.mode == 'RGBA':
                preview.paste(resized, (x_offset, y_offset), resized)
            else:
                preview.paste(resized, (x_offset, y_offset))
            x_offset += 256
        
        preview.save(preview_path)
        print(f"✓ Anteprima salvata: {preview_path}")
        
        print("\n" + "="*60)
        print("✅ ICONA MULTI-RISOLUZIONE CREATA CON SUCCESSO!")
        print("="*60)
        print(f"\n📍 File generato: {output_ico}")
        print(f"📊 Risoluzioni incluse: {len(sizes)} (da 256x256 a 16x16)")
        print(f"💡 L'icona sarà nitida a TUTTE le dimensioni in Windows!")
        print("\n🚀 Ora rigenera l'exe con: rebuild_exe.bat\n")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ ERRORE: File non trovato: {source_png}")
        print(f"   Assicurati che il file esista nella cartella assets/")
        return False
    except Exception as e:
        print(f"❌ ERRORE: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🎨 CREAZIONE ICONA MULTI-RISOLUZIONE")
    print("="*60)
    print()
    
    success = create_multisize_icon()
    
    if not success:
        exit(1)

