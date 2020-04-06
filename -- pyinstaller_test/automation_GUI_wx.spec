# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['automation_GUI_wx.py'],
             pathex=['C:\\Users\\Noah Baculi\\Documents\\Git\\automation\\pyinstaller_test'],
             binaries=[],
             datas=[('.\\logo.png', '.'), ('.\\logo.ico', '.'), ('.\\ctrl_keys_ref.csv', '.')],
             hiddenimports=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='automation_GUI_wx',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='logo.ico')
