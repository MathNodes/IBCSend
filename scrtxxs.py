'''
You need to edit the following variables below with your desired values:

WalletName  - Whatever you want to name the wallet in the keyring
HotWalletPW - Passowrd for your keyring
WalletSeed  - Seed if it is a new wallet, o/w it will pull from the keyring the WalletName

'''


import pwd
import os

import platform

pltform = platform.system()

if pltform == "Darwin":
    KeyringDIR         = "/Users/" + str(pwd.getpwuid(os.getuid())[0]) + "/.meile-ibc"
else:
    KeyringDIR         = "/home/" + str(pwd.getpwuid(os.getuid())[0]) + "/.meile-ibc"
    
WalletName         = ""
HotWalletPW        = ""
WalletSeed         = ""
GRPC               = "grpc.ungovernable.dev:443"
API                = "https://api.sentinel.mathnodes.com"
SSL                = True
        
