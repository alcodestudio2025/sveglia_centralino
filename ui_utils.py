"""
Utility per interfaccia grafica
"""
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

def add_logo_to_window(parent, row, column, window_width=1000):
    """
    Aggiunge il logo AL CODE STUDIO in basso a destra
    
    Args:
        parent: Frame genitore
        row: Riga nella griglia
        column: Colonna nella griglia
        window_width: Larghezza della finestra per scegliere dimensione logo
    """
    try:
        # Scegli dimensione logo in base alla larghezza finestra
        if window_width < 800:
            logo_file = 'assets/logo_small.png'
        elif window_width < 1200:
            logo_file = 'assets/logo_medium.png'
        else:
            logo_file = 'assets/logo_large.png'
        
        # Carica logo
        if os.path.exists(logo_file):
            logo_img = Image.open(logo_file)
            logo_photo = ImageTk.PhotoImage(logo_img)
            
            # Crea label per logo
            logo_label = ttk.Label(parent, image=logo_photo)
            logo_label.image = logo_photo  # Mantieni riferimento
            logo_label.grid(row=row, column=column, sticky=tk.SE, pady=(10, 5), padx=(0, 10))
            
            return logo_label
        
    except Exception as e:
        print(f"Impossibile caricare logo: {e}")
        return None

