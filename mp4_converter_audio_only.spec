# -*- mode: python ; coding: utf-8 -*-

import os

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

a = Analysis(
    [os.path.join(spec_dir, 'mp4_converter_standalone.py')],
    pathex=[spec_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'ffmpeg',
        'pathlib',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude Whisper and related AI packages to avoid build issues
        'whisper',
        'torch',
        'torchaudio', 
        'numpy',
        'soundfile',
        'numba',
        'llvmlite',
        'transformers',
        'tokenizers',
        'tensorflow',
        'tensorboard',
    ],
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
    name='mp4_converter_audio_only',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)