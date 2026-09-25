# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# Cross-platform path separator for datas
# PyInstaller uses semicolon on Windows, colon on Unix
sep = ';' if sys.platform == 'win32' else ':'
datas = [('assets', 'assets')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtMultimedia',
        'PySide6.QtGui',
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw'
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

# Windows / Linux single-file or macOS collection
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NekoDesk',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NekoDesk',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='NekoDesk.app',
        icon=None,
        bundle_identifier='com.nekodesk.app',
        info_plist={
            'LSUIElement': '1',  # Hide from Dock
            'NSHighResolutionCapable': 'True'
        }
    )
