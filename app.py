# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stockpy.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
import requests, os, json
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Ui_MainWindow(object):

    #stocklist = []
    def __init__(self):
        self.removewindow = RemoveWindow()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(792, 600)
        font = QtGui.QFont()
        font.setPointSize(8)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color:rgb(50, 58, 76);\n"
"selection-color: rgb(255, 255, 255);\n"
"border-color: rgb(16, 21, 33);\n"
"")
        MainWindow.setInputMethodHints(QtCore.Qt.ImhNone)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.setupUi(MainWindow)
        self.load()


    def load(self):
        if os.path.isfile("save.txt"):
            with open('save.txt', 'r') as f:
                temp = f.read()
                if os.path.getsize("save.txt") !=0:
                    self.stocklist = json.loads(temp)
            self.load_table()
        else:
            self.stocklist = []


    def getStock(self,symbol,region):

        key = os.getenv("API_KEY")
        host = "apidojo-yahoo-finance-v1.p.rapidapi.com"
        url =  "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
        headers = {"x-rapidapi-key": key, "x-rapidapi-host": host}
        params = {'symbols':symbol, 'region':region}

        
        response = requests.get(url, headers=headers, params = params)
        data = response.json()
        return(data["quoteResponse"]["result"][0]["regularMarketPrice"])


    def add_stock(self, text, price,qty):

        try:
            qty = int(qty)
            self.index = text.split(":")[0].upper()
            print(self.index)
            self.region = text.split(":")[1].upper()
            self.add_value = float(price) *qty
            self.updated_price = self.getStock(self.index,self.region)
            self.market_value = float(self.updated_price)*qty
            

            if not next((item for item in self.stocklist if item["index"] == self.index), False):
                tempdict = {}
                self.avgprice = float(price)
                self.pl = self.market_value - self.add_value
                tempdict["index"] = self.index
                tempdict["region"] = self.region
                tempdict["avgprice"] = self.avgprice
                tempdict["close_price"] = self.updated_price
                tempdict["qty"] = qty
                tempdict["pl"] = self.pl
                self.stocklist.append(tempdict.copy())
                
            else:
                #print("test")
                i = next((i for i, item in enumerate(self.stocklist) if item["index"] == self.index))
                self.stocklist[i]["avgprice"] = ((self.stocklist[i]["qty"] * self.stocklist[i]["avgprice"]) +self.add_value)/(self.stocklist[i]["qty"] + qty)
                self.stocklist[i]["qty"] += qty
                self.stocklist[i]["market_value"] = self.updated_price * self.stocklist[i]["qty"]
                self.stocklist[i]["pl"] = self.stocklist[i]["market_value"] - (self.stocklist[i]["avgprice"] * self.stocklist[i]["qty"])
                self.stocklist[i]["close_price"] = self.updated_price

            self.load_table()
            self.save()

        except:
            error = QtWidgets.QMessageBox()
            error.setWindowTitle("Input Error")
            error.setText("Please input a valid index, value or qty")
            error.setIcon(QtWidgets.QMessageBox.Information)
            x = error.exec_()

    def save(self):

        with open('save.txt', 'w') as f:
            f.write(json.dumps(self.stocklist))

    def remove(self,text,qty):
        #print("test")
        qty = int(qty)
        index = text.split(":")[0].upper()
        region = text.split(":")[1].upper()
        #print(self.stocklist)
        if next((item for item in self.stocklist if item["index"] == index), False):
            pos = next((i for i, item in enumerate(self.stocklist) if item["index"] == index))

            if self.stocklist[pos]["qty"]>=qty:
                self.stocklist[pos]["qty"] -= qty
                if self.stocklist[pos]["qty"] != 0:
                    self.stocklist[pos]["updated_price"] = self.getStock(index,region)
                    self.stocklist[pos]["market_value"] = self.stocklist[pos]["updated_price"]*self.stocklist[pos]["qty"]
                    self.stocklist[pos]["pl"] = self.stocklist[pos]["market_value"] - (self.stocklist[pos]["avgprice"]*self.stocklist[pos]["qty"])
                else:
                    self.stocklist = [i for i in self.stocklist if i.get("index") != index]
                self.save()
                self.load_table()
            else:
                error = QtWidgets.QMessageBox()
                error.setWindowTitle("Wrong index or qty")
                error.setText("Please input a valid index or qty")
                error.setIcon(QtWidgets.QMessageBox.Information)
                x = error.exec_()

        else:
            error = QtWidgets.QMessageBox()
            error.setWindowTitle("Wrong index or qty")
            error.setText("Please input a valid index or qty")
            error.setIcon(QtWidgets.QMessageBox.Information)
            x = error.exec_()

    def refresh(self):
        for x in self.stocklist:
            x["updated_price"] = self.getStock(x["index"],x["region"])
            x["market_value]"] = x["updated_price"] * x["qty"]
            x["pl"] = x["market_value"] - (x["avgprice"]*x["qty"])
        self.save()
        self.load_table()

    def load_table(self):

        row = 0
        self.stocktable.setRowCount(len(self.stocklist))
        for stock in self.stocklist:
            item = QtWidgets.QTableWidgetItem(stock["index"])
            item.setTextAlignment(Qt.AlignCenter)
            
            self.stocktable.setItem(row, 0, item)
            item = QtWidgets.QTableWidgetItem('{0:.2f}'.format(stock["close_price"]))
            item.setTextAlignment(Qt.AlignCenter)
            
            self.stocktable.setItem(row, 1, item)
            item = QtWidgets.QTableWidgetItem(str(stock["qty"]))
            item.setTextAlignment(Qt.AlignCenter)
            
            self.stocktable.setItem(row, 2, item)
            pl = QtWidgets.QTableWidgetItem('{0:.2f}'.format(stock["pl"]))
            pl.setTextAlignment(Qt.AlignCenter)
            
            if stock["pl"] >= 0: 
                pl.setForeground(QtGui.QBrush(QtGui.QColor(0,255,0)))
                self.stocktable.setItem(row, 3, QtWidgets.QTableWidgetItem(pl))
            else:
                pl.setForeground(QtGui.QBrush(QtGui.QColor(255,0,0)))
                self.stocktable.setItem(row, 3, QtWidgets.QTableWidgetItem(pl))
            row += 1

    def setupUi(self, MainWindow):

        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(30, 430, 731, 91))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label_index = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Coves")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_index.setFont(font)
        self.label_index.setStyleSheet("color: rgb(255, 255, 255)")
        self.label_index.setTextFormat(QtCore.Qt.AutoText)
        self.label_index.setAlignment(QtCore.Qt.AlignCenter)
        self.label_index.setObjectName("label_index")
        #self.label_index.move(0,5)
        self.gridLayout.addWidget(self.label_index, 0, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.frame)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.line.setFont(font)
        self.line.setLineWidth(3)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 0, 1, 2, 1)
        self.label_buyprice = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Coves")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_buyprice.setFont(font)
        self.label_buyprice.setStyleSheet("color: rgb(255, 255, 255)")
        self.label_buyprice.setTextFormat(QtCore.Qt.AutoText)
        self.label_buyprice.setAlignment(QtCore.Qt.AlignCenter)
        self.label_buyprice.setObjectName("label_buyprice")
        self.gridLayout.addWidget(self.label_buyprice, 0, 2, 1, 1)
        self.label_qty = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Coves")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_qty.setFont(font)
        self.label_qty.setStyleSheet("color: rgb(255, 255, 255)")
        self.label_qty.setTextFormat(QtCore.Qt.AutoText)
        self.label_qty.setAlignment(QtCore.Qt.AlignCenter)
        self.label_qty.setObjectName("label_qty")
        self.gridLayout.addWidget(self.label_qty, 0, 3, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.frame)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.line_2.setFont(font)
        self.line_2.setLineWidth(3)
        self.line_2.setMidLineWidth(0)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 0, 4, 2, 1)
        self.button_refresh = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_refresh.sizePolicy().hasHeightForWidth())
        self.button_refresh.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Coves")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.button_refresh.setFont(font)
        self.button_refresh.setStyleSheet("\n"
"color: rgb(255, 255, 255);")
        self.button_refresh.setObjectName("button_refresh")
        self.gridLayout.addWidget(self.button_refresh, 0, 5, 1, 1)
        self.lineEdit_index = QtWidgets.QLineEdit(self.frame)
        font = QtGui.QFont()
        font.setFamily("Open Sans")
        font.setPointSize(12)
        self.lineEdit_index.setFont(font)
        self.lineEdit_index.setStyleSheet("background: rgb(35, 40, 52);\n"
"foreground: rgb(203, 204, 198);\n"
"border: rgb(35, 40, 52);\n"
"color: rgb(255, 255, 255);")
        self.lineEdit_index.setText("")
        self.lineEdit_index.setObjectName("lineEdit_index")
        self.gridLayout.addWidget(self.lineEdit_index, 1, 0, 1, 1)
        self.lineEdit_price = QtWidgets.QLineEdit(self.frame)
        font = QtGui.QFont()
        font.setFamily("Open Sans")
        font.setPointSize(12)
        self.lineEdit_price.setFont(font)
        self.lineEdit_price.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lineEdit_price.setValidator(QtGui.QDoubleValidator(0,9999,2))
        self.lineEdit_price.setStyleSheet("background: rgb(35, 40, 52);\n"
"foreground: rgb(203, 204, 198);\n"
"border: rgb(35, 40, 52);\n"
"color: rgb(255, 255, 255);")
        self.lineEdit_price.setText("")
        self.lineEdit_price.setObjectName("lineEdit_price")
        self.gridLayout.addWidget(self.lineEdit_price, 1, 2, 1, 1)
        self.lineEdit_qty = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_qty.sizePolicy().hasHeightForWidth())
        self.lineEdit_qty.setSizePolicy(sizePolicy)
        self.lineEdit_qty.setMaximumSize(QtCore.QSize(50, 300))
        self.lineEdit_qty.setStyleSheet("background: rgb(35, 40, 52);\n"
"foreground: rgb(203, 204, 198);\n"
"border: rgb(35, 40, 52);\n"
"color: rgb(255, 255, 255);")
        self.lineEdit_qty.setObjectName("lineEdit_qty")
        self.gridLayout.addWidget(self.lineEdit_qty, 1, 3, 1, 1)
        self.lineEdit_qty.setValidator(QtGui.QIntValidator(0,9999))
        self.button_add = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setFamily("Coves")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.button_add.setFont(font)
        self.button_add.setStyleSheet("\n"
"color: rgb(255, 255, 255);")
        self.button_add.setObjectName("button_add")
        self.gridLayout.addWidget(self.button_add, 1, 5, 1, 1)

        #add button functionality
        self.button_add.clicked.connect(lambda: self.add_stock(self.lineEdit_index.text(),
                                        self.lineEdit_price.text(),self.lineEdit_qty.text()))

        self.button_remove = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_remove.sizePolicy().hasHeightForWidth())
        self.button_remove.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Coves")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.button_remove.setFont(font)
        self.button_remove.setStyleSheet("\n"
"color: rgb(255, 255, 255);")
        self.button_remove.setObjectName("button_remove")
        self.button_remove.clicked.connect(self.removewindow.display)
        self.gridLayout.addWidget(self.button_remove, 1, 6, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(20, 10, 741, 411))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.stocktable = QtWidgets.QTableWidget(self.frame_2)
        self.stocktable.setGeometry(QtCore.QRect(10, 50, 731, 331))
        self.stocktable.verticalHeader().setVisible(False)
        font = QtGui.QFont()
        font.setFamily("Open Sans")
        font.setPointSize(22)
        font.setBold(False)
        font.setWeight(50)
        self.stocktable.setFont(font)
        self.stocktable.setStyleSheet("background: rgb(35, 40, 52);\n"
"foreground: rgb(203, 204, 198);\n"
"border: rgb(35, 40, 52);\n" 
"color: rgb(255,255,255);\n"
"font-family: Open Sans;\n"
"text-align: center;\n"
"font-size: 14px;")
        self.stocktable.setRowCount(0)
        self.stocktable.setColumnCount(4)
        self.stocktable.setObjectName("stocktable")
        item = QtWidgets.QTableWidgetItem()
        self.stocktable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.stocktable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.stocktable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.stocktable.setHorizontalHeaderItem(3, item)
        self.stocktable.horizontalHeader().setVisible(True)
        self.stocktable.horizontalHeader().setCascadingSectionResizes(False)
        self.stocktable.horizontalHeader().setDefaultSectionSize(136)
        self.stocktable.horizontalHeader().setHighlightSections(True)
        self.stocktable.horizontalHeader().setSortIndicatorShown(True)
        self.stocktable.horizontalHeader().setStretchLastSection(True)
        self.stocktable.horizontalHeader().setStyleSheet("color: rgb(20, 25, 37);")
        self.stocktable.verticalHeader().setStretchLastSection(False)
        self.welcomelabel = QtWidgets.QLabel(self.frame_2)
        self.welcomelabel.setGeometry(QtCore.QRect(10, 10, 731, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.welcomelabel.sizePolicy().hasHeightForWidth())
        self.welcomelabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Coves")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.welcomelabel.setFont(font)
        self.welcomelabel.setAutoFillBackground(False)
        self.welcomelabel.setStyleSheet("color: rgb(255, 255, 255)")
        self.welcomelabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.welcomelabel.setFrameShadow(QtWidgets.QFrame.Plain)
        self.welcomelabel.setTextFormat(QtCore.Qt.PlainText)
        self.welcomelabel.setScaledContents(True)
        self.welcomelabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.welcomelabel.setWordWrap(True)
        self.welcomelabel.setObjectName("welcomelabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 792, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.load()
        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_index.setText(_translate("MainWindow", "Index:Region"))
        self.label_buyprice.setText(_translate("MainWindow", "Buy Price"))
        self.label_qty.setText(_translate("MainWindow", "QTY"))
        self.button_refresh.setText(_translate("MainWindow", "Refresh"))
        self.lineEdit_index.setPlaceholderText(_translate("MainWindow", "TSLA:US"))
        self.lineEdit_price.setPlaceholderText(_translate("MainWindow", "100.00"))
        self.button_add.setText(_translate("MainWindow", "Add Stock"))
        self.button_remove.setText(_translate("MainWindow", "Remove Stock"))
        self.stocktable.setSortingEnabled(True)
        item = self.stocktable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Index"))
        item.setTextAlignment(Qt.AlignHCenter)
        item = self.stocktable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Market Close Price"))
        item.setTextAlignment(Qt.AlignHCenter)
        item = self.stocktable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "QTY"))
        item.setTextAlignment(Qt.AlignHCenter)
        item = self.stocktable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Profit/Loss"))
        item.setTextAlignment(Qt.AlignHCenter)
        self.welcomelabel.setText(_translate("MainWindow", "Your Portfolio"))

class RemoveWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remove Stock")
        self.setMinimumSize(400,100)
        mainlayout = QtWidgets.QVBoxLayout()
        self.index = QtWidgets.QLineEdit()
        self.index.setPlaceholderText("TSLA:US")
        self.qty = QtWidgets.QLineEdit()
        self.qty.setValidator(QtGui.QIntValidator(0,9999))
        self.confirm = QtWidgets.QPushButton('Confirm')
        self.confirm.clicked.connect(self.passinfo)
        mainlayout.addWidget(QtWidgets.QLabel("Index:Region"))
        mainlayout.addWidget(self.index)
        mainlayout.addWidget(QtWidgets.QLabel("QTY:"))
        mainlayout.addWidget(self.qty)
        mainlayout.addWidget(self.confirm)
        self.setLayout(mainlayout)

    def passinfo(self):
        self.mainwindow = Ui_MainWindow()
        try:
            self.mainwindow.remove(self.index.text(),self.qty.text())
        except:
            error = QtWidgets.QMessageBox()
            error.setWindowTitle("Input Error")
            error.setText("Please input a valid index:region or qty")
            error.setIcon(QtWidgets.QMessageBox.Information)
            x = error.exec_()

    #def passinfo(self):


    def display(self):
        self.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)
    MainWindow.setWindowTitle("Stock Profit Tracker")
    MainWindow.show()
    sys.exit(app.exec_())




