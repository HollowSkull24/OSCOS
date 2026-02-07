# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/oscos/main.py'],
    pathex=[],
    binaries=[],
    datas=[
      ('src/oscos/resources/icons/OSCOS_icon.ico', 'resources/icons'),
      ('src/oscos/resources/icons/OSCOS_icon.png', 'resources/icons'),
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='OSCOS',
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
    icon=['src/oscos/resources/icons/OSCOS_icon.ico']
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='linux',
)
