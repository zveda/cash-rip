#!/usr/bin/env python3

import os, getpass
from electroncash.util import json_decode
from time import sleep
from tkinter import filedialog
from tkinter import *

Tk().withdraw()
wallet =  filedialog.askopenfilename(initialdir = "~/.electron-cash/wallets",title = "Select wallet")
print(wallet)
wp = getpass.getpass()
wp = "'"+wp+"'"
addrBig = input("Address to be broken up : ")
chunk = float(input("Chunk size[20] : ") or "20")

while True:
    bal = os.popen("electron-cash getaddressbalance "+addrBig).read()[:-1]
    bal = json_decode(bal)
    bal = float(bal['confirmed']) + float(bal['unconfirmed'])
    print('balance currently is: '+str(bal))
    if bal < chunk*1.2:
        print("All done.")
        break
    add = os.popen("electron-cash -w "+wallet+" getunusedaddress").read()[:-1]
    print("sending to: "+add)
    tx = os.popen("electron-cash -w "+wallet+" payto -F "+addrBig+" "+add+" "+str(chunk)+" -W "+wp).read()
    tx = json_decode(tx)
    #print(tx)
    deser = os.popen("electron-cash deserialize "+tx['hex']).read()[:-1]
    outputs = json_decode(deser)['outputs']
    #print("outputs: "+str(outputs))
    addrBig = outputs[1]['address'] if outputs[1]['value'] > outputs[0]['value'] else outputs[0]['address']
    
    os.system("electron-cash -w "+wallet+" broadcast "+tx['hex'])
    sleep(10)
