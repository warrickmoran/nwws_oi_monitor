# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../nww_oi_muc.py', '../nww_oi_muc_bot.py', '../nww_oi_rate.py', '../nww_oi_muc_stanza.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=['sleekxmpp.features', 'sleekxmpp.features.feature_starttls', 'sleekxmpp.features.feature_bind', 'sleekxmpp.features.feature_session', 'sleekxmpp.features.feature_bind', 'sleekxmpp.features.feature_rosterver', 'sleekxmpp.features.feature_mechanisms', 'sleekxmpp.features.feature_preapproval', 'sleekxmpp.plugins.xep_0004', 'sleekxmpp.plugins.xep_0030', 'sleekxmpp.plugins.xep_0045', 'sleekxmpp.plugins.xep_0199'],
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
          name='nww_oi_muc',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
