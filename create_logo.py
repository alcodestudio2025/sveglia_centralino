"""
Script per creare il logo AL CODE STUDIO
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(size=(200, 80)):
    """Crea il logo AL CODE STUDIO"""
    # Crea immagine con sfondo trasparente
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colori
    green = (0, 255, 100, 255)  # Verde brillante
    gray = (200, 200, 200, 255)  # Grigio chiaro
    
    # Calcola dimensioni font in base alla size
    al_font_size = int(size[1] * 0.5)
    text_font_size = int(size[1] * 0.2)
    
    try:
        # Prova a usare font del sistema
        al_font = ImageFont.truetype("arial.ttf", al_font_size)
        text_font = ImageFont.truetype("arial.ttf", text_font_size)
    except:
        # Fallback su font di default
        al_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Disegna "AL" in verde
    al_text = "AL"
    al_bbox = draw.textbbox((0, 0), al_text, font=al_font)
    al_width = al_bbox[2] - al_bbox[0]
    al_height = al_bbox[3] - al_bbox[1]
    al_x = (size[0] - al_width) // 2
    al_y = 5
    draw.text((al_x, al_y), al_text, fill=green, font=al_font)
    
    # Disegna "CODE STUDIO" sotto
    code_text = "CODE STUDIO"
    code_bbox = draw.textbbox((0, 0), code_text, font=text_font)
    code_width = code_bbox[2] - code_bbox[0]
    code_x = (size[0] - code_width) // 2
    code_y = al_y + al_height + 5
    draw.text((code_x, code_y), code_text, fill=gray, font=text_font)
    
    return img

if __name__ == "__main__":
    # Crea diverse dimensioni del logo
    sizes = {
        'small': (100, 40),
        'medium': (150, 60),
        'large': (200, 80)
    }
    
    os.makedirs('assets', exist_ok=True)
    
    for name, size in sizes.items():
        logo = create_logo(size)
        logo.save(f'assets/logo_{name}.png')
        print(f"[OK] Logo {name} creato: {size[0]}x{size[1]}px")
    
    print("\n[OK] Tutti i loghi creati con successo!")

