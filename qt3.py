#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys, threading, time

#from PyQt5.QtCore import pyqtSlot
#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import QFont, QIcon

# electron cash modules
'''
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'packages'))

import imp
imp.load_module('electroncash', *imp.find_module('lib'))
imp.load_module('electroncash_gui', *imp.find_module('gui'))
imp.load_module('electroncash_plugins', *imp.find_module('plugins'))
'''

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash import Network
from electroncash.bitcoin import COIN
from electroncash.address import Address, AddressError
from electroncash.plugins import BasePlugin, hook
from electroncash_gui.qt.util import EnterButton, Buttons, CloseButton, MessageBoxMixin, Buttons, MyTreeWidget, TaskThread
from electroncash_gui.qt.util import OkButton, WindowModalDialog
from electroncash.util import user_dir
import electroncash.version
from cashrip import CashRip

#sys.stderr = open('/dev/null', 'w')

class cashripQT(QWidget):

    def __init__(self, parent):
        super().__init__()
        #self.window = window
        self.parent = parent
        self.config = None
        self.cashRip = self.parent.cashRip
        self.title = 'CashRipQT'
        self.initUI()
    # qt.py and qt3.py are identical starting from this line until almost end of file, except for if __name__.
    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        #self.setToolTip('This is a <b>QWidget</b> widget')
        self.buttons = QHBoxLayout()

        btn1 = QPushButton('Create Contract', self)
        btn1.setToolTip('Creates a new contract.')
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.invite)
        self.buttons.addWidget(btn1)
        
        #btn.move(50, 50)
        btn2 = QPushButton('Accept Invite', self)
        btn2.setToolTip('Input: partner\'s <b>x_pubkey</b>.')
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.accInvite)
        self.buttons.addWidget(btn2)

        btn3 = QPushButton('Check Address', self)
        btn3.setToolTip('Input: your partner\'s generated multisig <b>address</b> and <b>x_pubkey</b>. Also select the <b>contract</b> you used to invite your partner.')
        btn3.resize(btn3.sizeHint())
        btn3.clicked.connect(self.checkAddress)
        self.buttons.addWidget(btn3)

        btn4 = QPushButton('Request Release', self)
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
        btn6.setToolTip('Delete selected <b>contract</b>. Do not delete any contract that still contains funds as you will then be unable to release those funds in the future.')
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

        #listWidget.currentItemChanged.connect(self.item_click)
        self.textArea1 = QLabel('Please select the contract you wish to use below.')
        #self.textArea2 = QLabel('Contract information (x_pubkey or transaction hex) goes in the box below.')
        self.textArea2 = QLabel('')
        self.textArea2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.textArea2.setStyleSheet("color: rgb(0, 0, 0);")
        self.textArea2.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        #self.textArea.setText('Please select the contract you wish to use above.\nContract information (x_pubkey or transaction hex) goes in the box below.')
        #self.textBox = QPlainTextEdit(self)
        #self.textBox.setPlainText('')
        '''
        self.addressBoxArea = QHBoxLayout()
        self.addressBox = QLineEdit(self)
        self.addrLabel = QLabel("Address:")
        self.addressBoxArea.addWidget(self.addrLabel)
        self.addressBoxArea.addWidget(self.addressBox)
        '''        

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textArea1)
        self.layout.addWidget(self.table) 
        #layout.addStretch(1)
        self.layout.addWidget(self.textArea2)
        #self.layout.addWidget(self.textBox) 
        #self.layout.addLayout(self.addressBoxArea)
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

    def getCurrentContract(self):
        item = self.table.currentItem()
        if item:
            return int(item.text(0))
        else:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);") 
            self.textArea2.setText("Please select a contract above, or create a new one via Create or Accept.")
            return None
    
    #@pyqtSlot()
    #def run_update(self):
    #    self.table.update()
    def clearTextArea(self):
        self.textArea2.setStyleSheet("color: rgb(0, 0, 0);") 
        self.textArea2.setText("")

    def invite(self):
        self.clearTextArea()
        buttonReply = QMessageBox.question(self, 'PyQt5 message', "This will create a new contract", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.textArea2.setText("Please wait . . .")
            self.textArea2.repaint()
            wallet, contract = self.cashRip.genContractWallet()
            contract["label"] = "buyer"
            self.cashRip.updateContracts()
            self.parent.update()
            self.textArea2.setText("Give this x_pubkey to the other party:\n{}".format(contract['my_x_pubkey']))
        else:
            return
    
    def accInvite(self):
        self.clearTextArea()
        text, ok = QInputDialog.getText(self, "Accept Invite","Your partner's x_pubkey:", QLineEdit.Normal, "")
        if ok:
            xpub = text
            #xpub = self.textBox.document().toPlainText()
            if xpub[:2] != "ff" or len(xpub) < 100:
                #self.textBox.setStyleSheet("background-color: rgb(255, 0, 0);")
                self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
                self.textArea2.setText("The x_pubkey that you entered is invalid.")
                return
            self.textArea2.setText("Please wait . . .")
            self.textArea2.repaint()
            wallet, contract = self.cashRip.genContractWallet()
            contract["label"] = "merchant"
            self.cashRip.updateContracts()
            idx = len(self.cashRip.contracts)-1
            try:
                contract = self.cashRip.create_multisig_addr(idx, xpub)
            except:
                self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
                self.textArea2.setText("Something was wrong with the x_pubkey you entered.")
                self.cashRip.delContract(idx)
                self.parent.update()
                return

            self.textArea2.setText("Your x_pubkey: {}\nYour multisig address: {}\nPlease share your x_pubkey and multisig address with your partner.".format(contract["my_x_pubkey"], contract["address"]))
            self.parent.update()
            #if self.textArea2.text()[:4] == "Your":
            self.cashRip.startSyncMultiWallet(idx)

    def checkAddress(self):
        self.clearTextArea()
        currentContract = self.getCurrentContract()
        if currentContract == None:
            return
        if "address" in self.cashRip.contracts[currentContract]:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("This contract already has an address. Maybe you selected the wrong contract?")
            return
        #text, ok = QInputDialog.getText(self, "Check Address","Your partner's x_pubkey:", QLineEdit.Normal, "")
        dialog = CheckAddressDialog(self)
        dialog.currentContract = currentContract
        dialog.show()
        #dialog.exec_()
        self.dialog = dialog
        #if dialog.exec_():

    def checkAddressAcc(self, dialog):
        #if a == QDialog.acccepted:
        #addrOrig = self.addressBox.text()
        addrOrig = dialog.address.text()
        try:
            addr = Address.from_string(addrOrig)
        except AddressError as e:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("The multisig address you entered is invalid.")
            return
        if addr.kind != Address.ADDR_P2SH:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("The address you entered was not a multisig address.")
            return

        xpub = dialog.xpub.text()
        if xpub[:2] != "ff" or len(xpub) < 100:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("The x_pubkey that you entered is invalid.")
            return

        #currentContract = self.getCurrentContract()
        currentContract = dialog.currentContract
        if self.cashRip.contracts[currentContract]["my_x_pubkey"] == xpub:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("You entered your own x_pubkey, not your partner's.")
            return   
        try: 
            self.textArea2.setText("Please wait . . .")
            self.textArea2.repaint()
            contract = self.cashRip.create_multisig_addr(currentContract, xpub, False)
        except:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("Something was wrong with the x_pubkey you pasted.")
            return
        if contract["address"] == addr:
            self.textArea2.setText("Success. You and your partner generated the same address. You can now send funds to {}".format(addrOrig))
            self.cashRip.startSyncMultiWallet(currentContract)
        else:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("Something went wrong. You and your partner generated different addresses. Please double-check the x_pubkeys that you have sent to each other.")
            os.remove(contract['addrWalletFile']) 
            del contract["addrWalletFile"]
            del contract["address"]
            del contract["partner_addr"]
            del contract["partner_x_pubkey"]
            del contract["partner_pubkey"]
            del contract["gen_by_me"]   
            del contract["redeemScript"]    
            self.cashRip.updateContracts()
            self.cashRip.multiWallets[currentContract] = None
        self.parent.update()

    def requestRelease(self):
        self.clearTextArea()
        currentContract = self.getCurrentContract()
        if currentContract == None:
            return
        if "address" not in self.cashRip.contracts[currentContract]:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("This contract does not have a multisig address yet.")
            return
        item = self.table.currentItem()
        balance = float(item.text(3))+float(item.text(4))
        if balance == 0:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("This contract has no funds yet.")
            return
        text, ok = QInputDialog.getText(self, "Request Release","Address to release funds to:", QLineEdit.Normal, "")
        if ok:
            addr = text
            try:
                #addr = Address.from_string(addr)
                addrCheck = Address.from_string(addr)
            except AddressError as e:
                self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
                self.textArea2.setText("The release address you entered was invalid.")
                return
            try:
                self.textArea2.setText("Please wait . . .")
                self.textArea2.repaint()
                tx = self.cashRip.maketx_from_multisig(currentContract, addr)
            except ValueError as e:
                self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
                self.textArea2.setText(str(e))
                return 
            # EC 3.3.1 needs output address to be Address object rather than String. Giving it String will cause AssertionError. TypeError is caused if you give Address object to EC 3.3.2 - this won't run for now.
            except (AssertionError,TypeError) as e: 
                #print(type(e)) 
                tx = self.cashRip.maketx_from_multisig(currentContract, addrCheck)
            self.textArea2.setText("Send this transaction hex to your partner. He needs it to release your funds:\n{}".format(tx['hex']))

    def release(self):
        self.clearTextArea()
        currentContract = self.getCurrentContract()
        if currentContract == None:
            return
        if "address" not in self.cashRip.contracts[currentContract]:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("This contract does not have a multisig address yet.")
            return
        item = self.table.currentItem()
        balance = float(item.text(3))+float(item.text(4))
        if balance == 0:
            self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
            self.textArea2.setText("This contract has no funds yet.")
            return
        text, ok = QInputDialog.getText(self, "Release","Transaction hex:", QLineEdit.Normal, "")
        if ok:
            txhex = text
            if len(txhex) < 150:
                self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
                self.textArea2.setText("The transaction hex you entered was too short.")
                return
            try:
                self.textArea2.setText("Please wait . . .")
                self.textArea2.repaint()
                sent = self.cashRip.sign_broadcast_tx_from_partner(txhex, currentContract)
                if sent:
                    self.textArea2.setText("Transaction was broadcast to the network.")
                else:
                    self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
                    self.textArea2.setText("Transaction was not broadcast. Either you selected the wrong contract or the transaction hex did not contain a valid signature.")
            except:
                self.textArea2.setStyleSheet("color: rgb(255, 0, 0);")
                self.textArea2.setText("Something went wrong. Maybe the hex value was invalid.")            

    def delContract(self):
        self.clearTextArea()
        currentContract = self.getCurrentContract()
        if currentContract == None:
            return
        curItem = self.table.currentItem()
        balC = curItem.text(3)
        balU = curItem.text(4)
        if curItem.text(2)[:4] != 'Wait' and (balC != "0.0" or balU != "0.0"):
            buttonReply = QMessageBox.question(self, 'Confirmation', "Are you sure you want to delete Contract #{}? It contains funds and you will be unable to release them in the future.".format(currentContract), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            buttonReply = QMessageBox.question(self, 'Confirmation', "Are you sure you want to delete Contract #{}?".format(currentContract), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.cashRip.delContract(currentContract)
            #self.table.update()
            self.parent.update()
        else:
            return

class CheckAddressDialog(QDialog):
    def __init__(self, parent):
        super(CheckAddressDialog, self).__init__()
        self.parent = parent
        self.createFormGroupBox()
 
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
 
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
 
        self.setWindowTitle("Check Address")
        self.resize(self.sizeHint())

    def accept(self):
        self.parent.checkAddressAcc(self)
        self.close()

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Check that your partner generated the multisig address correctly.")
        layout = QFormLayout()
        self.address = QLineEdit()
        self.xpub = QLineEdit()
        layout.addRow(QLabel("Address:"), self.address)
        layout.addRow(QLabel("Partner's x_pubkey:"), self.xpub)
        self.formGroupBox.setLayout(layout)

class cashRipList(MyTreeWidget):
    #filter_columns = [0, 2]
    def __init__(self, parent):
        self.columns = [ _("Index"), _("Label"),_("Address"), _("Confirmed"), _("Unconfirmed"), _("Your x_pubkey") ]
        MyTreeWidget.__init__(self, parent, self.create_menu, self.columns, 5, [1])
        self.cashRip = self.parent.parent.cashRip
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        #self.setColumnWidth(1,5000)

    def create_menu(self, position):
        menu = QMenu()
        selected = self.selectedItems()
        names = [item.text(0) for item in selected]
        keys = [item.text(1) for item in selected]
        column = self.currentColumn()
        column_title = self.headerItem().text(column)
        column_data = '\n'.join([item.text(column) for item in selected])
        menu.addAction(_("Copy {}").format(column_title), lambda: QApplication.clipboard().setText(column_data))
        if column in self.editable_columns:
            item = self.currentItem()
            menu.addAction(_("Edit {}").format(column_title), lambda: self.editItem(item, column))
        #run_hook('create_contact_menu', menu, selected)
        menu.exec_(self.viewport().mapToGlobal(position))

    def on_edited(self, item, column, prior):
        label = item.text(1)
        if len(label) > 40:
            label = label[:50]
        for c in self.cashRip.contracts:
            if c["my_x_pubkey"] == item.text(5):
                c["label"] = label
                self.cashRip.updateContracts()
                self.update()
                return

    def on_update(self):
        #print("Updating tables")
        #standard, multi = self.cashRip.getContractWalletBalances()
        multi = self.cashRip.getMultiBalances()
        item = self.currentItem()
        current_id = int(item.text(0)) if item else None
        self.clear()
        items = []
        for i,c in enumerate(self.cashRip.contracts):
            if "address" in c:
                addr = c['address'].to_ui_string()
                values = [str(i), c["label"], addr, str(multi[addr][0]/COIN), str(multi[addr][1]/COIN), c["my_x_pubkey"]]
                item = QTreeWidgetItem(values)
                self.addTopLevelItem(item)
            else:
                item = QTreeWidgetItem([str(i), c["label"], "Wait for partner to send address.", None, None, c["my_x_pubkey"]])
                self.addTopLevelItem(item)
            if i == current_id:
                self.setCurrentItem(item)
    
class SignalDummy(QObject):
    update_signal = pyqtSignal()

class Plugin(BasePlugin):

    def fullname(self):
        return 'cash_rip'

    def description(self):
        return _("Configure CashRip Protocol")

    def is_available(self):
        return True

    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)
        self.windows = []
        self.tabs = []
        self.cashRip = None
        self.config = config
        
        self.signal_dummy = SignalDummy()
        self.signal_dummy.update_signal.connect(self.update)
        #self.tableUpdater = threading.Thread(target=self.updateTableLoop)
        #self.tableUpdater.daemon = True
        self.keepUpdating = True
        self.tableUpdater = TaskThread(self.signal_dummy)
        self.tableUpdater.add(self.updateTableLoop)
        self.tableUpdater.start()
        #self.wallet_windows = {}

    @hook
    def init_qt(self, gui):
        # We get this multiple times.  Only handle it once, if unhandled.
        if self.windows:
            return
        for window in gui.windows:
            self.load_wallet(window.wallet, window)
    
    def updateTableLoop(self):
        while self.keepUpdating:
            time.sleep(6)
            self.signal_dummy.update_signal.emit()

    @hook
    def load_wallet(self, wallet, window):
        """
        Hook called when a wallet is loaded and a window opened for it.
        """
        if self.cashRip == None:
            topDir = os.path.join(self.config.path, 'cash_rip_data')
            self.cashRip = CashRip(topDir, window.network)
        self.windows.append(window)
        tab = cashripQT(window, self)
        self.tabs.append(tab)
        #self.tab.set_coinshuffle_addrs()
        icon = QIcon(":icons/tab_coins.png")
        description =  _("Cash Rip")
        name = "Cash Rip"
        tab.tab_icon = icon
        tab.tab_description = description
        #self.tab.tab_pos = len(self.window.tabs)
        tab.tab_name = name
        window.tabs.addTab(tab, icon, description.replace("&", ""))

    @hook
    def on_close_window(self, window):
        idx = self.windows.index(window)
        #tab = self.tabs[idx]
        del self.windows[idx]
        #tab.tableUpdater.stop()
        #tab.keepUpdating = False
        del self.tabs[idx]

    def on_close(self):
        """
        BasePlugin callback called when the plugin is disabled among other things.
        """
        for idx,w in enumerate(self.windows):
            tab = self.tabs[idx]
            tabIndex = w.tabs.indexOf(tab)
            w.tabs.removeTab(tabIndex)
        self.tableUpdater.stop()
        self.keepUpdating = False
        self.windows.clear()
        self.tabs.clear()
    
    #@pyqtSlot()
    def update(self):
        for tab in self.tabs:
            tab.table.update()
            
    def requires_settings(self):
        return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    p = Plugin(None, None, None)
    network = Network(None)
    network.start()
    p.cashRip = CashRip('./cash_rip_data', network)
    ex = cashripQT(p)
    p.tabs.append(ex)
    sys.exit(app.exec_())
