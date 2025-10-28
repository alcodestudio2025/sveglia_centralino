"""
Script per creare il logo AL CODE STUDIO basato sull'immagine fornita dall'utente
Riproduce fedelmente: sfondo nero con pattern binario, AL verde, CODE STUDIO grigio
"""
from PIL import Image, ImageDraw, ImageFont
import os
import random

def create_binary_background(size, density=0.3):
    """Crea uno sfondo con pattern binario verde tipo Matrix"""
    img = Image.new('RGBA', size, (0, 0, 0, 255))  # Sfondo nero
    draw = ImageDraw.Draw(img)
    
    # Verde del pattern binario (più scuro del verde AL)
    binary_green = (0, 180, 60, 80)  # Verde scuro con trasparenza
    
    try:
        font = ImageFont.truetype("consolas.ttf", 8)
    except:
        try:
            font = ImageFont.truetype("courier.ttf", 8)
        except:
            font = ImageFont.load_default()
    
    # Riempie lo sfondo con 0 e 1 casuali
    rows = size[1] // 10
    cols = size[0] // 8
    
    for row in range(rows):
        for col in range(cols):
            if random.random() < density:
                digit = random.choice(['0', '1'])
                x = col * 8
                y = row * 10
                draw.text((x, y), digit, fill=binary_green, font=font)
    
    return img

def create_logo_with_matrix(size=(200, 80)):
    """Crea il logo AL CODE STUDIO con sfondo Matrix binario"""
    # Crea sfondo con pattern binario
    img = create_binary_background(size)
    draw = ImageDraw.Draw(img)
    
    # Colori esatti dall'immagine
    green_al = (0, 255, 100, 255)  # Verde brillante per AL
    gray_text = (200, 200, 200, 255)  # Grigio chiaro per CODE STUDIO
    
    # Calcola dimensioni font
    al_font_size = int(size[1] * 0.55)
    text_font_size = int(size[1] * 0.16)
    
    try:
        # Font bold per AL
        al_font = ImageFont.truetype("arialbd.ttf", al_font_size)
        text_font = ImageFont.truetype("arial.ttf", text_font_size)
    except:
        try:
            al_font = ImageFont.truetype("arial.ttf", al_font_size)
            text_font = ImageFont.truetype("arial.ttf", text_font_size)
        except:
            al_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    
    # Disegna "AL" in verde brillante al centro-alto
    al_text = "AL"
    al_bbox = draw.textbbox((0, 0), al_text, font=al_font)
    al_width = al_bbox[2] - al_bbox[0]
    al_height = al_bbox[3] - al_bbox[1]
    al_x = (size[0] - al_width) // 2
    al_y = int(size[1] * 0.12)
    
    # Ombra molto sottile per profondità
    draw.text((al_x + 1, al_y + 1), al_text, fill=(0, 0, 0, 200), font=al_font)
    draw.text((al_x, al_y), al_text, fill=green_al, font=al_font)
    
    # Disegna "CODE STUDIO" sotto (una riga sola)
    code_text = "CODE STUDIO"
    code_bbox = draw.textbbox((0, 0), code_text, font=text_font)
    code_width = code_bbox[2] - code_bbox[0]
    code_x = (size[0] - code_width) // 2
    code_y = al_y + al_height + int(size[1] * 0.1)
    
    draw.text((code_x + 1, code_y + 1), code_text, fill=(0, 0, 0, 150), font=text_font)
    draw.text((code_x, code_y), code_text, fill=gray_text, font=text_font)
    
    return img

if __name__ == "__main__":
    # Crea diverse dimensioni del logo
    sizes = {
        'small': (120, 50),
        'medium': (180, 75),
        'large': (240, 100)
    }
    
    os.makedirs('assets', exist_ok=True)
    
    for name, size in sizes.items():
        logo = create_logo_with_matrix(size)
        logo.save(f'assets/logo_{name}.png')
        print(f"[OK] Logo Matrix {name} creato: {size[0]}x{size[1]}px")
    
    print("\n[OK] Loghi con stile Matrix creati con successo!")

