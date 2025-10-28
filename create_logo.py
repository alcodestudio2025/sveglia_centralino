"""
Script per creare il logo AL CODE STUDIO
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(size=(200, 80)):
    """Crea il logo AL CODE STUDIO con sfondo e bordo"""
    # Crea immagine con sfondo scuro
    img = Image.new('RGBA', size, (40, 40, 45, 255))  # Sfondo grigio scuro
    draw = ImageDraw.Draw(img)
    
    # Colori migliorati
    green = (0, 255, 100, 255)  # Verde brillante
    gray = (220, 220, 220, 255)  # Grigio molto chiaro
    border_color = (60, 60, 65, 255)  # Bordo leggermente più chiaro
    
    # Disegna bordo sottile
    border_width = 2
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=border_color, width=border_width)
    
    # Calcola dimensioni font in base alla size
    al_font_size = int(size[1] * 0.45)
    text_font_size = int(size[1] * 0.18)
    
    try:
        # Prova a usare font del sistema (bold per AL)
        al_font = ImageFont.truetype("arialbd.ttf", al_font_size)  # Arial Bold
        text_font = ImageFont.truetype("arial.ttf", text_font_size)
    except:
        try:
            # Fallback su arial normale
            al_font = ImageFont.truetype("arial.ttf", al_font_size)
            text_font = ImageFont.truetype("arial.ttf", text_font_size)
        except:
            # Ultimo fallback
            al_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    
    # Disegna "AL" in verde con ombra per contrasto
    al_text = "AL"
    al_bbox = draw.textbbox((0, 0), al_text, font=al_font)
    al_width = al_bbox[2] - al_bbox[0]
    al_height = al_bbox[3] - al_bbox[1]
    al_x = (size[0] - al_width) // 2
    al_y = int(size[1] * 0.15)
    
    # Ombra nera per contrasto
    shadow_offset = 2
    draw.text((al_x + shadow_offset, al_y + shadow_offset), al_text, fill=(0, 0, 0, 180), font=al_font)
    # Testo verde brillante
    draw.text((al_x, al_y), al_text, fill=green, font=al_font)
    
    # Disegna "CODE STUDIO" sotto con spaziatura
    code_text = "CODE STUDIO"
    code_bbox = draw.textbbox((0, 0), code_text, font=text_font)
    code_width = code_bbox[2] - code_bbox[0]
    code_x = (size[0] - code_width) // 2
    code_y = al_y + al_height + int(size[1] * 0.08)
    
    # Ombra per contrasto
    draw.text((code_x + 1, code_y + 1), code_text, fill=(0, 0, 0, 180), font=text_font)
    # Testo grigio chiaro
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

