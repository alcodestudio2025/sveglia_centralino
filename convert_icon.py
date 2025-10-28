"""
Converte icona_3.png in .ico per l'exe
"""
from PIL import Image
import os

def convert_to_ico():
    """Converte PNG in ICO per Windows executable"""
    if not os.path.exists('assets/icona_3.png'):
        print("Errore: icona_3.png non trovata in assets/")
        return
    
    try:
        # Apri l'immagine
        img = Image.open('assets/icona_3.png')
        
        # Crea versioni multiple per diverse dimensioni
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_imgs = []
        
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_imgs.append(resized)
        
        # Salva come .ico
        icon_imgs[0].save('assets/app_icon.ico', format='ICO', sizes=[s for s in sizes])
        print(f"[OK] Icona .ico creata: assets/app_icon.ico")
        print(f"[OK] Dimensioni incluse: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        
    except Exception as e:
        print(f"Errore nella conversione: {e}")

if __name__ == "__main__":
    convert_to_ico()

