# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import os

playwright_datas = collect_data_files("playwright")
playwright_hiddenimports = [
    "playwright._impl._driver",
    "playwright.sync_api"
]

a = Analysis(
    ['html_to_gif_gui_playwright.py'],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=playwright_datas,
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
    a.binaries,  # <- jetzt enthalten!
    a.zipfiles,
    a.datas,     # <- jetzt enthalten!
    [],
    name='html_to_gif_gui_playwright',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
