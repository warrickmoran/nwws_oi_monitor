# nwws_oi_monitor


## Executable creation using pyinstaller 

Note:
spec file must include: 
hiddenimports=['sleekxmpp.features', 'sleekxmpp.features.feature_starttls', 'sleekxmpp.features.feature_bind', 'sleekxmpp.features.feature_session', 'sleekxmpp.features.feature_bind', 'sleekxmpp.features.feature_rosterver', 'sleekxmpp.features.feature_mechanisms', 'sleekxmpp.features.feature_preapproval', 'sleekxmpp.plugins.xep_0004', 'sleekxmpp.plugins.xep_0030', 'sleekxmpp.plugins.xep_0045', 'sleekxmpp.plugins.xep_0199'],
            
* mkdir deployment
* cd deployment
* pyinstaller -F nww_oi_muc.spec 


## Command Line Execution 

`./dist/nww_oi_muc --jid=<user id> --password=<password>`

## Command Line Execution with Visualization

`./dist/nww_oi_muc --jid=<user id> --password=<password> --metrics`
