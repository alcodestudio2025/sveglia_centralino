"""
Crea un'icona semplice e pulita per l'exe
Ottimizzata per Windows con dimensioni standard
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_simple_icon():
    """Crea un'icona semplice e pulita per l'exe"""
    
    # Dimensione massima per l'icona (256x256 è lo standard Windows)
    size = 256
    
    # Sfondo gradiente dal nero al grigio scuro
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Crea un gradiente radiale
    for i in range(size):
        for j in range(size):
            # Distanza dal centro
            dx = i - size/2
            dy = j - size/2
            distance = (dx*dx + dy*dy) ** 0.5
            max_distance = (size/2) * 1.4
            
            # Colore basato sulla distanza
            factor = max(0, 1 - distance / max_distance)
            r = int(20 + factor * 20)
            g = int(20 + factor * 20)
            b = int(25 + factor * 25)
            
            img.putpixel((i, j), (r, g, b, 255))
    
    # Disegna un cerchio di sfondo più chiaro
    circle_color = (45, 45, 50, 255)
    margin = 30
    draw.ellipse([margin, margin, size-margin, size-margin], fill=circle_color)
    
    # Colori
    green = (0, 255, 100, 255)  # Verde brillante
    gray = (220, 220, 220, 255)
    
    # Font sizes
    try:
        # Prova Arial Bold
        main_font = ImageFont.truetype("arialbd.ttf", 100)
        sub_font = ImageFont.truetype("arial.ttf", 28)
    except:
        try:
            main_font = ImageFont.truetype("arial.ttf", 100)
            sub_font = ImageFont.truetype("arial.ttf", 28)
        except:
            main_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
    
    # Disegna "AL" grande al centro in verde
    al_text = "AL"
    al_bbox = draw.textbbox((0, 0), al_text, font=main_font)
    al_width = al_bbox[2] - al_bbox[0]
    al_height = al_bbox[3] - al_bbox[1]
    al_x = (size - al_width) // 2
    al_y = (size - al_height) // 2 - 20
    
    # Ombra per profondità
    shadow_offset = 3
    draw.text((al_x + shadow_offset, al_y + shadow_offset), al_text, 
              fill=(0, 0, 0, 200), font=main_font)
    draw.text((al_x, al_y), al_text, fill=green, font=main_font)
    
    # Disegna "SVEGLIE" piccolo sotto
    sub_text = "SVEGLIE"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_x = (size - sub_width) // 2
    sub_y = al_y + al_height + 15
    
    draw.text((sub_x + 1, sub_y + 1), sub_text, fill=(0, 0, 0, 180), font=sub_font)
    draw.text((sub_x, sub_y), sub_text, fill=gray, font=sub_font)
    
    return img

def save_as_ico():
    """Salva l'icona in formato .ico con multiple dimensioni"""
    
    # Crea l'icona base
    base_img = create_simple_icon()
    
    # Dimensioni standard per .ico
    sizes = [
        (16, 16),   # Piccola (menu)
        (32, 32),   # Media (barra)
        (48, 48),   # Grande (vista icone)
        (64, 64),   # Extra (alta risoluzione)
        (128, 128), # Vista dettagli
        (256, 256)  # Massima (Windows 10/11)
    ]
    
    # Crea versioni ridimensionate
    images = []
    for size in sizes:
        resized = base_img.resize(size, Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Salva come .ico multi-size
    os.makedirs('assets', exist_ok=True)
    images[0].save(
        'assets/app_icon.ico',
        format='ICO',
        sizes=sizes,
        append_images=images[1:]
    )
    
    # Salva anche PNG per preview
    base_img.save('assets/app_icon_preview.png')
    
    print("[OK] Icona .ico creata: assets/app_icon.ico")
    print(f"[OK] Dimensioni incluse: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
    print("[OK] Preview PNG salvata: assets/app_icon_preview.png")

if __name__ == "__main__":
    save_as_ico()

