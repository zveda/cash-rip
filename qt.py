#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, threading, time
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
import cash_rip
from electroncash import Network
from electroncash.bitcoin import COIN
from electroncash.address import Address
sys.stderr = open('/dev/null', 'w')

contracts = cash_rip.contracts

class cashrip(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Cash_Rip'
        self.left = 300
        self.top = 300
        self.width = 640
        self.height = 480
        self.network = Network(None)
        self.network.start()
        self.initUI()
    
    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is a <b>QWidget</b> widget')
        self.buttons = QHBoxLayout()

        btn1 = QPushButton('Invite', self)
        btn1.setToolTip('This is a <b>InitiateContract</b> widget')
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.invite)
        self.buttons.addWidget(btn1)
        
            #btn.move(50, 50)
        btn2 = QPushButton('AcceptInvite', self)
        btn2.setToolTip('This is a <b>InitiateContract</b> widget')
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.accInvite)
        self.buttons.addWidget(btn2)

        btn3 = QPushButton('CheckAddress', self)
        btn3.setToolTip('This is a <b>InitiateContract</b> widget')
        btn3.resize(btn3.sizeHint())
        btn3.clicked.connect(self.checkAddress)
        self.buttons.addWidget(btn3)

        btn4 = QPushButton('RequestRelease', self)
        btn4.setToolTip('This is a <b>InitiateContract</b> widget')
        btn4.resize(btn4.sizeHint())
        btn4.clicked.connect(self.requestRelease)
        self.buttons.addWidget(btn4)


        btn5 = QPushButton('Release', self)
        btn5.setToolTip('This is a <b>InitiateContract</b> widget')
        btn5.resize(btn5.sizeHint())
        btn5.clicked.connect(self.release)
        self.buttons.addWidget(btn5)

        btn6 = QPushButton('Delete Contract', self)
        btn6.setToolTip('This is a <b>InitiateContract</b> widget')
        btn6.resize(btn6.sizeHint())
        btn6.clicked.connect(self.delContract)
        self.buttons.addWidget(btn6)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemClicked.connect(self.table_click)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Address;Confirmed;Unconfirmed;x_pubkey").split(";"))
        #self.table.horizontalHeaderItem().setTextAlignment(Qt.AlignHCenter)
        self.updateTable()
        self.tableUpdater = threading.Thread(target=self.updateTableLoop)
        self.tableUpdater.daemon = True
        self.tableUpdater.start()
        #listWidget.currentItemChanged.connect(self.item_click)
        self.textArea = QLabel("Here is some text.")
        self.textArea.setText('Contract information goes in the box below.')
        self.textBox = QPlainTextEdit(self)
        self.textBox.setPlainText('')
        #s = self.textBox.document().toPlainText()
        #print(s)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table) 
        #layout.addStretch(1)
        self.layout.addWidget(self.textArea)
        self.layout.addWidget(self.textBox) 
        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout) 
         
        #self.layout.move(100,100)
        #self.listWidget.show()
        self.setWindowTitle('Cash Rip')
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(self.width, self.height)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def table_click(self, item):
        #print(item.text())
        #print(self.currentRow())
        print(self.table.currentRow())

    def updateTableLoop(self):
        while True:
            self.updateTable()
            time.sleep(10)

    def updateTable(self):
        print("Updating tables")
        self.table.setRowCount(len(contracts))
        labels = ''
        for i in range(len(contracts)):
            labels = labels + 'Contract '+str(i)+';' 
        self.table.setVerticalHeaderLabels((labels).split(";"))
        standard, multi = cash_rip.getContractWalletBalances(self.network)
        for i,c in enumerate(contracts):
            if "address" in c:
                addr = c['address'].to_ui_string()
                item1 = QTableWidgetItem(addr)
                item2 = QTableWidgetItem(str(multi[addr][0]/COIN))
                item3 = QTableWidgetItem(str(multi[addr][1]/COIN))
                
                #self.table.setItem(i, 0, QTableWidgetItem("Contract {}".format(i)))
                self.table.setItem(i, 0, item1)
                self.table.setItem(i, 1, item2)
                self.table.setItem(i, 2, item3)
            else:
                item = QTableWidgetItem("Wait for partner to send address.")
                self.table.setItem(i, 0, item)  
   
            item4 = QTableWidgetItem(c["my_x_pubkey"])
            self.table.setItem(i, 3, item4)

    @pyqtSlot()
    def invite(self):
        wallet, contract = cash_rip.genContractWallet()
        self.updateTable()
        self.textBox.setPlainText("Give this x_pubkey to the other party:\n{}".format(contract['my_x_pubkey']))
    
    def accInvite(self):
        wallet, contract = cash_rip.genContractWallet()
        contract = cash_rip.create_multisig_addr(len(contracts)-1, self.textBox.document().toPlainText())
        self.textBox.setPlainText("Your x_pubkey: {}\n Partner x_pubkey: {}\nYou can now send funds to the multisig address {}\nThis will tear your bitcoin cash in half.".format(contract["my_x_pubkey"], contract["partner_x_pubkey"], contract["address"]))
        self.updateTable()

    def checkAddress(self):
        args = self.textBox.document().toPlainText().split()
        contract = cash_rip.create_multisig_addr(self.table.currentRow(), args[1], False)
        if contract["address"].to_ui_string() == args[0]:
            self.textBox.setPlainText("Success. You and your partner generated the same address. You can now send funds to {}".format(args[0]))
        else:
            self.textBox.setPlainText("Something went wrong. You and your partner generated different addresses. Please double-check the x_pubkeys that you have sent to each other.")        
        self.updateTable()

    def requestRelease(self):
        tx = cash_rip.maketx_from_multisig(self.table.currentRow(), Address.from_string(self.textBox.document().toPlainText()), self.network)
        self.textBox.setPlainText("Send this transaction hex to your partner. He needs it to release your funds:\n{}".format(tx['hex']))

    def release(self):
        cash_rip.sign_broadcast_tx_from_partner(self.textBox.document().toPlainText(), self.table.currentRow(), self.network)

    def delContract(self):
        #print(self.table.currentRow())
        cash_rip.delContract(self.table.currentRow())
        self.updateTable()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = cashrip()
    sys.exit(app.exec_())
