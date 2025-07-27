# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import os

# Nur noch Playwright-Daten (ohne Browser)
playwright_datas = collect_data_files("playwright")
playwright_hiddenimports = [
    "playwright._impl._driver",
    "playwright.sync_api"
]

a = Analysis(
    ['html_to_gif_gui_playwright.py'],
    pathex=[os.path.abspath(".")],
    binaries=[],                 # ← leer lassen
    datas=playwright_datas,      # ← keine Browserdaten mehr nötig
    hiddenimports=playwright_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='html_to_gif_gui_playwright',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # ← auf False setzen, wenn GUI-only (kein Terminalfenster)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
