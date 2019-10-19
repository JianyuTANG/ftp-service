# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'inputDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 266)
        self.Input = QtWidgets.QLineEdit(Dialog)
        self.Input.setGeometry(QtCore.QRect(52, 100, 301, 41))
        self.Input.setObjectName("Input")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 50, 301, 16))
        self.label.setObjectName("label")
        self.okbutton = QtWidgets.QPushButton(Dialog)
        self.okbutton.setGeometry(QtCore.QRect(160, 180, 93, 28))
        self.okbutton.setObjectName("okbutton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "TextLabel"))
        self.okbutton.setText(_translate("Dialog", "OK"))

