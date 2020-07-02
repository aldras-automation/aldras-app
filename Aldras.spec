# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Aldras.py'],
             pathex=['C:\\Users\\Noah Baculi\\Documents\\Git\\aldras'],
             binaries=[],
             datas=[('LexActivator.dll', '.'), ('./data', 'data')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Aldras',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='data\\Aldras.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Aldras')
