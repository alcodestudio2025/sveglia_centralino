# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Lista di tutti i file dati da includere
datas = [
    ('assets', 'assets'),
    ('audio_messages', 'audio_messages'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PIL',
        'PIL._imaging',
        'pydub',
        'pygame',
        'paramiko',
        'sqlite3',
        'tkinter',
        'tkinter.ttk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Wakeup_Manager_v_2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Finestra console nascosta
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon_2.ico',  # Icona dell'applicazione (exe, start bar, title bar)
    version='version_info.txt',  # Metadati versione e informazioni produttore
)

