# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/derhami/Converterz/Converterz.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Converterz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/derhami/Converterz/logo.icns'],
)
app = BUNDLE(
    exe,
    name='Converterz.app',
    icon='/Users/derhami/Converterz/logo.icns',
    bundle_identifier=None,
)
