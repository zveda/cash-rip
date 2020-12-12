#!/usr/bin/env python3

import os
from electroncash.util import json_decode
from tkinter import filedialog
from tkinter import *

Tk().withdraw()
wallet =  filedialog.askopenfilename(initialdir = "~/.electron-cash/wallets",title = "Select wallet")

coins = os.popen("electron-cash -w "+wallet+" listunspent").read()
coins = json_decode(coins)
#print(coins)
addrValues = {}

for c in coins:
    addrValues.setdefault(c['address'], []).append(c['value'])

for ad in addrValues:
    numVals = len(addrValues[ad])
    if numVals > 1:
        numDust = 0
        for i in range(numVals):
            if addrValues[ad][i] == '0.00000547':
                numDust += 1
        if numVals - numDust > 1:
            print(ad, numVals, addrValues[ad])

