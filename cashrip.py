#!/usr/bin/env python3
# -*- mode: python -*-
#
#MIT License

#Copyright (c) 2018 zveda

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from electroncash.address import Address
from electroncash.storage import WalletStorage
from electroncash.wallet import Wallet, ImportedAddressWallet
from electroncash.mnemonic import Mnemonic
from electroncash.util import print_msg, json_encode, json_decode
from electroncash import SimpleConfig, Network, keystore, commands
from electroncash.bitcoin import COIN
from contextlib import redirect_stdout, redirect_stderr
import sys, copy, os
#from electroncash.networks import NetworkConstants
#NetworkConstants.set_testnet()
#f = open('/dev/null', 'w')
#sys.stderr = f

topDir = '.'

def genContractWallet(nickname=None):
    if not os.path.isdir(topDir +'/wallets'):
        os.mkdir(topDir+'/wallets')
    if nickname:
        for i,c in enumerate(contracts):
            if c["nickname"] == nickname:
                print("{} contract exists.".format(nickname))
                return getContractWallet(i), c
    #print(type(contracts))
    #this next loop generates a wallet name that isn't in use yet. 
    if contracts == []:
        walletFile = topDir +'/wallets/contract0.wallet'
    else: 
        walletNames = []
        for c in contracts:
            #print(c)
            walletNames.append(c['walletFile'])
        for i in range(len(walletNames)+1):
            walletFile = topDir +'/wallets/contract'+str(i)+'.wallet'
            if walletFile not in walletNames:
                break
    storage = WalletStorage(walletFile)
    seed_type = 'standard'
    seed = Mnemonic('en').make_seed(seed_type)
    k = keystore.from_seed(seed, '', False)
    storage.put('keystore', k.dump())
    storage.put('wallet_type', 'standard')
    wallet = Wallet(storage)
    wallet.update_password(None, '', True)
    wallet.synchronize()
    print_msg("Your wallet generation seed is:\n\"%s\"" % seed)
    print_msg("Please keep it in a safe place; if you lose it, you will not be able to restore your wallet.")

    wallet.storage.write()
    print_msg("Wallet saved in '%s'" % wallet.storage.path)

    my_addr = wallet.get_unused_address()
    my_addr_index = wallet.receiving_addresses.index(my_addr)
#my_addr_index is always going to be 0 if the wallet is unused, so maybe previous line unnecessary
    my_pubkey = wallet.derive_pubkeys(False, my_addr_index)
    my_x_pubkey = get_x_pubkey(my_addr_index, wallet)
    contracts.append({'walletFile': wallet.storage.path, "my_addr": my_addr, "my_pubkey": my_pubkey, "my_x_pubkey": my_x_pubkey, "nickname": nickname})
    #print(contracts)
    updateContracts()
    return wallet, contracts[-1]

def delContract(idx):
    os.remove(contracts[idx]['walletFile'])
    if 'address' in contracts[idx]:
        os.remove(contracts[idx]['addrWalletFile'])
    del contracts[idx]
    updateContracts()

def updateContracts():
#    if contracts == '' or contracts == []:
#        print_message("Contracts list is empty. Something went wrong.")
#        return
    contracts2 = copy.deepcopy(contracts)
    for c in contracts2:
        c["my_addr"] = c["my_addr"].to_ui_string()
        if "address" in c:
            c["address"] = c["address"].to_ui_string()
            c["partner_addr"] = c["partner_addr"].to_ui_string()
            
    f = open(topDir +'/contracts.txt', 'w')
    f.write(json_encode(contracts2))
    f.close()

def backupContract(c):
    c2 = copy.deepcopy(c)
    c2["my_addr"] = c2["my_addr"].to_ui_string()
    if "address" in c2:
        c2["address"] = c2["address"].to_ui_string()
        c2["partner_addr"] = c2["partner_addr"].to_ui_string()
    f = open(topDir +'/contracts-bkp.txt', 'a')
    f.write(json_encode(c2))
    f.close()    

def loadContracts():
    try:
        f = open(topDir +'/contracts.txt', 'r')
    except:
        print('No contracts found.')
        return []
    contracts = json_decode(f.read())
    for c in contracts:
        c["my_addr"] = Address.from_string(c["my_addr"])
        if "address" in c:
            c["address"] = Address.from_string(c["address"])
            c["partner_addr"] = Address.from_string(c["partner_addr"])
    #print(contracts)
    #contracts = json.loads(contracts)
    f.close()
    if contracts == '':
        return []
    else:
        return contracts

contracts = loadContracts()

def getContractWallet(idx):
    storage = WalletStorage(contracts[idx]['walletFile'])
    if storage.file_exists():
        wallet = Wallet(storage)
        return wallet

def getAddressWallet(idx):
    storage = WalletStorage(contracts[idx]['addrWalletFile'])
    if storage.file_exists():
        wallet = Wallet(storage)
        return wallet    

def getContractWalletBalances(network):
    balancesStandard = {}
    balancesMulti = {}
    for i,con in enumerate(contracts):
        wal = getContractWallet(i)
        wal.start_threads(network)
        wal.synchronize()
        wal.wait_until_synchronized()
        #c = commands.Commands(None, wal, network)
        #print(type(c.getbalance()))
        #print_msg("=======================wallet up to date: %s" % wal.is_up_to_date())
        #print_msg("=======================Contract %s has balance: %s" % (i, wal.get_balance()))
        balancesStandard[con['walletFile']] = wal.get_balance()
        if "address" in con.keys():
            #c = commands.Commands(None, wal, network)
            #addr = con["address"].to_ui_string()
            #balancesMulti[addr] = c.getaddressbalance(addr)
            wal2 = getAddressWallet(i)
            wal2.start_threads(network)
            wal2.synchronize()
            wal2.wait_until_synchronized()
            balancesMulti[con['address'].to_ui_string()] = wal2.get_balance()
    return balancesStandard, balancesMulti

def get_tx_size(tx):
    return int(len(tx['hex'])/2)

def get_x_pubkey(addr_index, wallet):
    #pubkey = wallet.derive_pubkeys(False, addr_index)
    #return wallet.xpub_from_pubkey(pubkey)
    xp = keystore.Xpub()
    xp.xpub = wallet.get_master_public_key()
    return xp.get_xpubkey(False, addr_index)

def testImportedAddrWallet(addrStr):
    network = Network(None)
    network.start()
    storage = WalletStorage(topDir +'/wallets/test.wallet')
    wal = ImportedAddressWallet.from_text(storage, addrStr)
    print(wal)
    wal.start_threads(network)
    wal.synchronize()
    wal.wait_until_synchronized()
    bal = wal.get_balance()
    print(bal)


#idx is contract index    
#if generated_by_me is False, partner must have generated the address, so we are checking the address was generated correctly. my_pubkey and partner_pubkey must be in different order. 
def create_multisig_addr(idx, partner_x_pubkey, generated_by_me=True):
    wallet = getContractWallet(idx)
    c = commands.Commands(None, wallet, None)
    contract = contracts[idx]

    if 'address' in contract:
        print_msg("**********************************Overwriting old contract. It will be saved in contracts-bkp.txt")
        backupContract(contract)
        
    (partner_pubkey, partner_address) = keystore.xpubkey_to_address(partner_x_pubkey)
    if generated_by_me:
        multiaddress = c.createmultisig(2, [contract["my_pubkey"], partner_pubkey])
    else:
        multiaddress = c.createmultisig(2, [partner_pubkey, contract["my_pubkey"]])
    multiaddress["address"] = Address.from_string(multiaddress["address"])

    contract.update(multiaddress)
    contract["partner_addr"] = partner_address
    contract["partner_x_pubkey"] = partner_x_pubkey
    contract["partner_pubkey"] = partner_pubkey
    contract["gen_by_me"] = generated_by_me

    addrWalletFile = contract["walletFile"][:-7]+"-address.wallet"
    #print("addrWalletFile: {}".format(addrWalletFile))
    storage = WalletStorage(addrWalletFile)
    if storage.file_exists():
        os.remove(addrWalletFile)
        storage = WalletStorage(addrWalletFile)
    wal = ImportedAddressWallet.from_text(storage, contract["address"].to_ui_string())
    wal.synchronize()
    wal.storage.write()
    print_msg("Wallet saved in '%s'" % wal.storage.path)
    contract["addrWalletFile"] = addrWalletFile
    #print_msg("contracts now: %s" % contracts)
    updateContracts()
    return contract
    
    
#idx is contract index, to_addr is Address object
def maketx_from_multisig(idx, to_addr, network):
    #initial_params = {'num_sig': 2, 'sequence': 4294967294, 'signatures': [None, None], 'type': 'p2sh'}
    contract = contracts[idx]
    if "address" not in contract:
        raise Exception("This contract does not have a multisig address yet. Generate one first.")
        #sys.exit()    
    wallet = getContractWallet(idx)
    walletAddr = getAddressWallet(idx)
    c = commands.Commands(None, wallet, network)
    address_str = contract['address'].to_ui_string()
    #addr_balance = c.getaddressbalance(address_str)
    #total_balance = float(addr_balance['confirmed'])+float(addr_balance['unconfirmed'])
    #total_balance = int(total_balance*COIN)
    (standard, multis) = getContractWalletBalances(network)
    #print(multis)
    total_balance = sum(multis[address_str])
    print("********************************total balance: {}".format(total_balance))
    if total_balance == 0:
        return False
    #hist = c.getaddresshistory(address_str) 
    utxos = walletAddr.get_utxos()
    #print("********************************hist is: {}".format(hist))
    #print("********************************utxos is: {}".format(utxos))
    '''prev_relevant_outputs = []
    for tx in hist:
        fulltx = c.gettransaction(tx["tx_hash"])
        fulltx = c.deserialize(fulltx) 
        for output in fulltx['outputs']:
            if output["address"].to_ui_string() == address_str:
                output["prevout_hash"] = tx["tx_hash"]
                prev_relevant_outputs.append(output)
    print("********************************prev_relevant_outputs is: {}".format(prev_relevant_outputs))'''
    inp = []
    for output in utxos:
        inp.append( {"value": output["value"], 
                    "prevout_n": output["prevout_n"], 
                    "prevout_hash": output["prevout_hash"], 
                    "type": "p2sh", "address": output["address"], 
                    "num_sig": 2, 
                    "signatures": [None, None], 
                    "sequence": 4294967294, 
                    "redeemScript": contract["redeemScript"], 
                    "pubkeys": [contract["my_pubkey"], contract["partner_pubkey"]], 
                    "x_pubkeys": [contract["my_x_pubkey"], contract["partner_x_pubkey"]]})
    if not contract['gen_by_me']:
        for i in inp:
            i["pubkeys"] = [contract["partner_pubkey"], contract["my_pubkey"]]
            i["x_pubkeys"] = [contract["partner_x_pubkey"], contract["my_x_pubkey"]]
    outp = [{        "type": 0, 
                    "address": to_addr, 
                    "value": total_balance-500, 
                    "prevout_n": 0}]
    tx = {"version":1, "lockTime":0, "outputs": outp, "inputs": inp}
    print(tx)
    txS = c.serialize(tx)
    fee = get_tx_size(txS)*2    # we multiply the size by 2 because we are not sure how much bigger the partner's signature will make the transaction. But it should not double it in size. Fee should be less than 2 satoshis/byte.
    tx["outputs"][0]["value"] = int(total_balance-fee)     
    #print(tx["outputs"][0]["value"])
    print("********************************tx fee will be {}".format(fee))
    txS = c.serialize(tx)
    #print (c.deserialize(txS))
    signedtx = c.signtransaction(txS)
    #print("signing once")
    return signedtx

'''Here we assume our partner has sent us a transaction signed by him. We just need to sign it and broadcast'''
def sign_broadcast_tx_from_partner(tx, my_wallet_index, network):
    wallet1 = getContractWallet(my_wallet_index)
    c = commands.Commands(None, wallet1, network)
    txSigned = c.signtransaction(tx)
    #print_msg("size is: %s" % get_tx_size(txSigned))
    #print(c.deserialize(txSigned))
    c.broadcast(txSigned)
    print("Transaction of size {} bytes has been broadcast.".format(get_tx_size(txSigned)))

def test():
    stor = WalletStorage('/home/ilia/.electron-cash/wallets/default_wallet')
    wal = Wallet(stor)
    stor2 = WalletStorage('/home/ilia/.electron-cash/wallets/test_wallet')
    wal2 = Wallet(stor2)
    c = commands.Commands(None, wal, None)
    c2 = commands.Commands(None, wal2, None)

    ao = Address.from_string("qq6cqr5sxgzrnrdfl62hrfy88pfhe89egqyld9nnj7")
    #ao = "qq6cqr5sxgzrnrdfl62hrfy88pfhe89egqyld9nnj7"    
    ai = Address.from_string("pqjdgep0cmscpvrk3n7euqqlqfmwk2770uagtjgcl5")
    #ai = "pqjdgep0cmscpvrk3n7euqqlqfmwk2770uagtjgcl5"

    outp = [{"type": 0, "address": ao, "value": 39500, "prevout_n": 0}]

    inp = [{"address": ai, "num_sig": 2, "sequence": 4294967294, "signatures": [None,None], "value": 40000, "type": "p2sh", "redeemScript": "522103ad9164b6e6d94602f25823196f3a35d9b9afb7622223c7d5ee7bc8f17e7ca0bb2102a6ef7ee97b10e0d5866cf972c9fa8f0b0954d13d5a49423d3941fc0a71021eef52ae", "prevout_hash": "7451d7d947716f1fe3ed973c9a2cbebb5952c22fa0a4685b8331d2ffc37e23ce", "x_pubkeys": ["ff0488b21e000000000000000000833b2b39ca3b1aedcc76ebc2dd54f2201e3f8ceb7fa16fbe4341249e24c0a8af03b55587668eac88a678b564e7bf7368b6ae32d04fa1d7dc252a596a7925779a0200000100", "ff0488b21e000000000000000000fd897a1c33cf038d108419d73559aba5ba26a8c1b7952ae6ff65be21a78be1a102f4eb32dc585e2585967369b6618771c1dce8dc928d996042bef2c80782ac408300000000"], "pubkeys": ["03ad9164b6e6d94602f25823196f3a35d9b9afb7622223c7d5ee7bc8f17e7ca0bb", "02a6ef7ee97b10e0d5866cf972c9fa8f0b0954d13d5a49423d3941fc0a71021eef"], "prevout_n": 0}]

    y={"version":1, "lockTime":0, "outputs": outp, "inputs": inp}
    tx = c.serialize(y)
    #print(tx)
    w = c.deserialize(c.serialize(y))
    #print(w['inputs'][0]['address'])
    #print(c.deserialize(tx))
    tx2 = c.signtransaction(tx)
    #print(c.deserialize(tx2))
    tx3 = c2.signtransaction(tx2)
    print(c.deserialize(tx3))
    print(get_tx_size(tx3))
    print(get_tx_size(tx2))
    print(get_tx_size(tx))
    #print(tx3)
'''Commands takes arguments config, wallet, network'''

#def deleteContract():

def test2():
    network = Network(None)
    network.start()
    #wallet = genContractWallet()
    #wallet1 = genContractWallet()
    #print(len(contracts))
    wallet1 = getContractWallet(1)

    partner_x_pubkey = get_x_pubkey(0, wallet1)
    #print_msg("partner xpubkey: %s" % partner_x_pubkey)
    create_multisig_addr(0, partner_x_pubkey)
    print(getContractWalletBalances(network))

def test3():
    network = Network(None)
    network.start()
    to_addr = Address.from_string("bitcoincash:qqj4pf98k326u53ns75ap7lm4xp7a9upyc9nwcxrun")
    tx = maketx_from_multisig(0, to_addr, network)
    print_msg("Are we broadcasting tx?: {}".format(tx))
    #if tx:
    #    sign_broadcast_tx_from_partner(tx, 1)

def testImportedAddrWallet(addrStr):
    network = Network(None)
    network.start()
    storage = WalletStorage(topDir +'/wallets/test.wallet')
    wal = ImportedAddressWallet.from_text(storage, addrStr)
    print(wal)
    wal.start_threads(network)
    wal.synchronize()
    wal.wait_until_synchronized()
    bal = wal.get_balance()
    print(bal)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Implement Cash-Rip using multisignature wallets.")
    #group = parser.add_mutually_exclusive_group()
    #parser.add_argument("-cn", "--contractnick", type=str, help="Contract nickname of either new or existing contract. If no or new nickname provided, a new contract will be created.")
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    subparsers.required = True

    parser_listcontracts = subparsers.add_parser('listcontracts', help='List your created contracts and their states.')

    parser_gencontract = subparsers.add_parser('gencontract', help='Create a contract.')

    parser_delcontract = subparsers.add_parser('delcontract', help='Delete a contract. Input: contract index.')
    parser_delcontract.add_argument('contractindex', type=int, help='Contract index that you want to delete.')

    parser_genmultisig = subparsers.add_parser('genmultisig', help='Create a multisig address. Takes as input the contractindex of one of your created contracts, as well as partner\'s x_pubkey')
    parser_genmultisig.add_argument('contractindex', type=int, help='Your contract index that you want to use.')
    parser_genmultisig.add_argument('x_pubkey', type=str, help="partner's x_pubkey")

    parser_checkaddress = subparsers.add_parser('checkaddress', help='Check the multisig address your partner generated. Takes as input the contractindex of your relevant contract (that contains the x_pubkey you first sent your partner), the address your partner generated, and his x_pubkey')
    parser_checkaddress.add_argument('contractindex', type=int, help='Your contract index that you want to use.')
    parser_checkaddress.add_argument('address', type=str, help="multisig address your partner generated and sent you")
    parser_checkaddress.add_argument('x_pubkey', type=str, help="partner's x_pubkey")

    parser_requestrelease = subparsers.add_parser('requestrelease', help='Ask the buyer to release the coins to you by sending him the result of this command. Inputs: contractindex, to_address (where the coins will be released to).')
    parser_requestrelease.add_argument('contractindex', type=int, help='requestrelease help')
    parser_requestrelease.add_argument('to_address', type=str, help='requestrelease help')    

    parser_release = subparsers.add_parser('release', help='Release the coins to seller. Requires contractindex and the transaction_hex generated by your partner with the requestrelease command.')
    parser_release.add_argument('contractindex', type=int, help='genmultisig help')
    parser_release.add_argument('transaction_hex', type=str, help='genmultisig help')
    #parser.set_defaults(command='listcontracts')

    args = parser.parse_args()
    #print(args)    
    #print(parser_genmultisig)
    #if args.contractnick:
    #    wallet, contract = genContractWallet(args.contractnick)
    #    idx = contracts.index(contract)    
    sys.stderr = open('/dev/null', 'w')
    #f = open('/dev/null', 'w')    

    if args.command == 'listcontracts':
    #with redirect_stderr(f):
        network = Network(None)
        network.start()
        standard, multi = getContractWalletBalances(network)
        network.stop()
        #print(multi)
        #print(standard, multi)
        for i,c in enumerate(contracts):
            if 'address' in c:
                addr = c['address'].to_ui_string()
                print("Contract index: {}\taddress: {}\tbalance: confirmed {} BCH, unconfirmed {} BCH\t".format(i, addr, multi[addr][0]/COIN, multi[addr][1]/COIN) ) 
            else:
                print("Contract index: {}\t No multisig address generated yet.".format(i)) 
    elif args.command == 'gencontract':
    #with redirect_stderr(f):
        wallet, contract = genContractWallet()
        print("Give this x_pubkey to the other party:\n {}".format(contract['my_x_pubkey']))

    elif args.command == 'delcontract':
        #print(args.contractindex, type(args.contractindex))
        delContract(args.contractindex)

    elif args.command == 'genmultisig': 
        #with redirect_stderr(f):
        contract = create_multisig_addr(args.contractindex, args.x_pubkey)
        print("\nAddress: {}\n Your x_pubkey: {}\n Partner x_pubkey: {}\n".format(contract["address"], contract["my_x_pubkey"], contract["partner_x_pubkey"]))
        print("You can now send funds to the multisig address {} This will tear your bitcoin cash in half.".format(contract["address"]))

    elif args.command == 'checkaddress':
        #with redirect_stderr(f):
        contract = create_multisig_addr(args.contractindex, args.x_pubkey, False)    
        if contract["address"].to_ui_string() == args.address:
            print("Success. You and your partner generated the same address. You can now send funds to {}".format(args.address))
        else:
            print("Something went wrong. You and your partner generated different addresses. Please double-check the x_pubkeys that you have sent to each other.")

    elif args.command == 'requestrelease':
    #with redirect_stderr(f):
        network = Network(None)
        network.start()
        tx = maketx_from_multisig(args.contractindex, Address.from_string(args.to_address), network)

        print("Send this transaction hex to your partner. He needs it to release your funds:")
        print(tx['hex'])

    elif args.command == 'release':
        #with redirect_stderr(f):
        network = Network(None)
        network.start()
        #c = commands.Commands(None, None, network) #delet later
        #print(c.deserialize(args.transaction_hex))
        sign_broadcast_tx_from_partner(args.transaction_hex, args.contractindex, network)
        
if __name__ == '__main__':
    main()
    #test3()
    #testImportedAddrWallet("ppssl66pryy3d34cd7feccjw69pdds4luqc3qkvx63")

#test2()

#(c,i) -- c is whether I want change address. i is index of address -- often 0,0
