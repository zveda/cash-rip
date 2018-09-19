#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, threading, time

#from PyQt5.QtCore import pyqtSlot
#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import QFont, QIcon

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash import Network
from electroncash.bitcoin import COIN
from electroncash.address import Address
from electroncash.plugins import BasePlugin, hook
from electroncash_gui.qt.util import EnterButton, Buttons, CloseButton, MessageBoxMixin, Buttons, MyTreeWidget, TaskThread
#from electroncash_gui.qt.util import *
from electroncash_gui.qt.util import OkButton, WindowModalDialog
from electroncash.util import user_dir
import electroncash.version, os
import cashrip

sys.stderr = open('/dev/null', 'w')

class cashripQT(QWidget):

    update_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.window = window
        self.config = None
        self.title = 'CashRipQT'
        self.network = Network(None)
        self.network.start()
        cashrip.topDir = './cash_rip_data'
        if not os.path.isdir(cashrip.topDir):
            os.mkdir(cashrip.topDir)
        cashrip.contracts = cashrip.loadContracts()
        self.contracts = cashrip.contracts
        #print(len(self.contracts))
        self.initUI()
    
    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        #self.setToolTip('This is a <b>QWidget</b> widget')
        self.buttons = QHBoxLayout()

        btn1 = QPushButton('Invite', self)
        btn1.setToolTip('Creates a new contract.')
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.invite)
        self.buttons.addWidget(btn1)
        
            #btn.move(50, 50)
        btn2 = QPushButton('AcceptInvite', self)
        btn2.setToolTip('Input: partner\'s <b>x_pubkey</b>.')
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.accInvite)
        self.buttons.addWidget(btn2)

        btn3 = QPushButton('CheckAddress', self)
        btn3.setToolTip('Input: your partner\'s generated multisig <b>address</b> and <b>x_pubkey</b>. Also select the <b>contract</b> you used to invite your partner.')
        btn3.resize(btn3.sizeHint())
        btn3.clicked.connect(self.checkAddress)
        self.buttons.addWidget(btn3)

        btn4 = QPushButton('RequestRelease', self)
        btn4.setToolTip('Input:  BCH <b>address</b> to which the funds will be released. Also select your <b>contract</b> that contains the funds to be released.')
        btn4.resize(btn4.sizeHint())
        btn4.clicked.connect(self.requestRelease)
        self.buttons.addWidget(btn4)


        btn5 = QPushButton('Release', self)
        btn5.setToolTip('Input: <b>hex code</b> sent by your partner. Also select your <b>contract</b> that contains the funds to be released.')
        btn5.resize(btn5.sizeHint())
        btn5.clicked.connect(self.release)
        self.buttons.addWidget(btn5)

        btn6 = QPushButton('Delete Contract', self)
        btn6.setToolTip('Delete selected <b>contract</b>. Do not delete any contract that still contains funds as you will then not be able to release those funds in the future.')
        btn6.resize(btn6.sizeHint())
        btn6.clicked.connect(self.delContract)
        self.buttons.addWidget(btn6)

        self.table = cashRipList(self)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        #self.table.itemClicked.connect(self.table_click)
        #self.table.setColumnCount(4)
        #self.table.setHorizontalHeaderLabels(("Address;Confirmed;Unconfirmed;x_pubkey").split(";"))
        #self.table.setColumnWidth(3,230)
        #self.table.horizontalHeaderItem().setTextAlignment(Qt.AlignHCenter)
        self.table.update()
        self.update_signal.connect(self.run_update)
        #self.tableUpdater = threading.Thread(target=self.updateTableLoop)
        #self.tableUpdater.daemon = True
        self.tableUpdater = TaskThread(self)
        self.tableUpdater.add(self.updateTableLoop)
        self.tableUpdater.start()
        #listWidget.currentItemChanged.connect(self.item_click)
        self.textArea = QLabel("Here is some text.")
        self.textArea.setText('Please select the contract you wish to use above.\nContract information (x_pubkey or transaction hex) goes in the box below.')
        self.textBox = QPlainTextEdit(self)
        self.textBox.setPlainText('')
        #s = self.textBox.document().toPlainText()
        #print(s)
        self.addressBoxArea = QHBoxLayout()
        self.addressBox = QLineEdit(self)
        self.addrLabel = QLabel("Address:")
        self.addressBoxArea.addWidget(self.addrLabel)
        self.addressBoxArea.addWidget(self.addressBox)
        

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table) 
        #layout.addStretch(1)
        self.layout.addWidget(self.textArea)
        self.layout.addWidget(self.textBox) 
        self.layout.addLayout(self.addressBoxArea)
        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout) 
         
        #self.layout.move(100,100)
        #self.listWidget.show()
        self.setWindowTitle('Cash Rip')
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(self.sizeHint())
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def table_click(self, item):
        pass
        #print(item.text())
        #print(self.currentRow())
        #print(self.table.currentRow())

    def updateTableLoop(self):
        while True:
            #self.table.update()
            self.update_signal.emit()
            time.sleep(10)

    def getCurrentContract(self):
        item = self.table.currentItem()
        if item:
            return int(item.text(0))
        else:
            self.textBox.setPlainText("Please select a contract above, or create a new one via Invite or Accept.")
            return None
    
    @pyqtSlot()
    def run_update(self):
        self.table.update()

    def invite(self):
        #TODO:
        #self.textBox.setPlainText("Please wait . . .")
        wallet, contract = cashrip.genContractWallet()
        contract["label"] = "buyer"
        cashrip.updateContracts()
        self.table.update()
        self.textBox.setPlainText("Give this x_pubkey to the other party:\n{}".format(contract['my_x_pubkey']))
    
    def accInvite(self):
        xpub = self.textBox.document().toPlainText()
        if xpub[:2] != "ff" or len(xpub) < 100:
            self.textBox.setPlainText("Please enter your partner's x_pubkey into this textbox before clicking AcceptInvite.")
            return
        self.textBox.setPlainText("Please wait . . .")
        wallet, contract = cashrip.genContractWallet()
        contract["label"] = "merchant"
        cashrip.updateContracts()
        try:
            contract = cashrip.create_multisig_addr(len(self.contracts)-1, xpub)
            self.textBox.setPlainText("Your x_pubkey: {}\n Partner x_pubkey: {}\nYou can now send funds to the multisig address {}\nThis will tear your bitcoin cash in half.".format(contract["my_x_pubkey"], contract["partner_x_pubkey"], contract["address"]))
            self.table.update()
        except:
            self.textBox.setPlainText("Something was wrong with the x_pubkey you pasted.")
            cashrip.delContract(len(self.contracts)-1)
            self.table.update()

    def checkAddress(self):
        xpub = self.textBox.document().toPlainText()
        if xpub[:2] != "ff" or len(xpub) < 100:
            self.textBox.setPlainText("Please enter your partner's x_pubkey into this textbox before clicking CheckAddress.")
            return
        addr = self.addressBox.text()
        try:
            Address.from_string(addr)
        except:
            self.addressBox.setText("Please enter multisig address here before clicking CheckAddress.")
            return
        currentContract = self.getCurrentContract()
        if currentContract != None:
            if "address" in self.contracts[currentContract]:
                self.textBox.setPlainText("This contract already has an address.")
                return
            if self.contracts[currentContract]["my_x_pubkey"] == xpub:
                self.textBox.setPlainText("You entered your own x_pubkey, not your partner's.")
                return   
            try: 
                contract = cashrip.create_multisig_addr(currentContract, xpub, False)
            except:
                self.textBox.setPlainText("Something was wrong with the x_pubkey you pasted.")
                return
            if contract["address"].to_ui_string() == addr:
                self.textBox.setPlainText("Success. You and your partner generated the same address. You can now send funds to {}".format(addr))
            else:
                self.textBox.setPlainText("Something went wrong. You and your partner generated different addresses. Please double-check the x_pubkeys that you have sent to each other.")
                os.remove(contract['addrWalletFile']) 
                del contract["addrWalletFile"]
                del contract["address"]
                del contract["partner_addr"]
                del contract["partner_x_pubkey"]
                del contract["partner_pubkey"]
                del contract["gen_by_me"]   
                del contract["redeemScript"]    
                cashrip.updateContracts()
            self.table.update()

    def requestRelease(self):
        addr = self.addressBox.text()
        try:
            addr = Address.from_string(addr)
        except:
            self.addressBox.setText("Please enter address here before clicking RequestRelease.")
            return
        currentContract = self.getCurrentContract()
        if currentContract != None:
            tx = cashrip.maketx_from_multisig(currentContract, addr, self.network)
            if tx:
                self.textBox.setPlainText("Send this transaction hex to your partner. He needs it to release your funds:\n{}".format(tx['hex']))
            else:
                self.textBox.setPlainText("Something didn't work. Perhaps the selected contract has no funds.")

    def release(self):
        txhex = self.textBox.document().toPlainText()
        if len(txhex) < 150:
            self.textBox.setPlainText("Please enter the transaction hex into this box before hitting Release.")
            return
        currentContract = self.getCurrentContract()
        if currentContract != None:
            try:
                sent = cashrip.sign_broadcast_tx_from_partner(txhex, currentContract, self.network)
                if sent:
                    self.textBox.setPlainText("Transaction was broadcast to the network.")
                else:
                    self.textBox.setPlainText("Transaction was not broadcast. Either you selected the wrong contract or the transaction hex did not contain a valid signature.")
            except:
                self.addressBox.setText("Something went wrong. Maybe the hex value was invalid.")            

    def delContract(self):
        currentContract = self.getCurrentContract()
        #print(currentContract)
        if currentContract != None:
            cashrip.delContract(currentContract)
            self.table.update()

class cashRipList(MyTreeWidget):
    #filter_columns = [0, 2]
    def __init__(self, parent):
        self.columns = [ _("Index"), _("Label"),_("Address"), _("Confirmed"), _("Unconfirmed"), _("x_pubkey") ]
        MyTreeWidget.__init__(self, parent, self.create_menu, self.columns, 5, [1])
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        #self.setColumnWidth(1,5000)
        #self.itemSelectionChanged.connect(self.onItemSelectionChanged)

    def on_edited(self, item, column, prior):
        label = item.text(1)
        if len(label) > 40:
            label = label[:50]
        for c in self.parent.contracts:
            if c["my_x_pubkey"] == item.text(5):
                c["label"] = label
                cashrip.updateContracts()
                self.update()
                return

    def on_update(self):
        #print("Updating tables")
        standard, multi = cashrip.getContractWalletBalances(self.parent.network)
        item = self.currentItem()
        current_id = int(item.text(0)) if item else None
        
        #self.setCurrentItem(None)
        #time.sleep(0.1)
        self.clear()
        items = []
        for i,c in enumerate(self.parent.contracts):
            if "address" in c:
                addr = c['address'].to_ui_string()
                values = [str(i), c["label"], addr, str(multi[addr][0]/COIN), str(multi[addr][1]/COIN), c["my_x_pubkey"]]
                item = QTreeWidgetItem(values)
                #self.setItem(i, 0, QTableWidgetItem("Contract {}".format(i)))
                self.addTopLevelItem(item)
                #self.setItem(i, 1, item2)
                #self.setItem(i, 2, item3)
            else:
                item = QTreeWidgetItem([str(i), c["label"], "Wait for partner to send address.", None, None, c["my_x_pubkey"]])
                self.addTopLevelItem(item)
            if i == current_id:
                self.setCurrentItem(item)
    def create_menu(self, position):
        pass
    
    #def onItemSelectionChanged(self):
    #    pass

class Plugin(BasePlugin):

    def fullname(self):
        return 'cash_rip'

    def description(self):
        return _("Configure CashRip Protocol")

    def is_available(self):
        return True

    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)
        self.window = None
        self.tab = None

    @hook
    def init_qt(self, gui):
        for window in gui.windows:
            self.on_new_window(window)

    @hook
    def on_new_window(self, window):
        self.update(window)

    @hook
    def on_close_window(self, window):
        self.update(window)

    def on_close(self):
        tabIndex= self.window.tabs.indexOf(self.tab)
        self.window.tabs.removeTab(tabIndex)

    def update(self, window):
        self.window = window
        self.tab = cashripQT(window)
        #self.tab.set_coinshuffle_addrs()
        icon = QIcon(":icons/tab_coins.png")
        description =  _("Cash Rip")
        name = "rip"
        self.tab.tab_icon = icon
        self.tab.tab_description = description
        self.tab.tab_pos = len(self.window.tabs)
        self.tab.tab_name = name
        self.window.tabs.addTab(self.tab, icon, description.replace("&", ""))

    def requires_settings(self):
        return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = cashripQT()
    sys.exit(app.exec_())
