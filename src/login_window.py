from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from polito_sync import PolitoWebClass
from PyQt5.QtWidgets import QMessageBox
from subjects_window import SubjectsWindow

import sys


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self,session):
        super(LoginWindow, self).__init__()
        self.session = session

        uic.loadUi('loginUI.ui', self)

        self.LoginButton = self.findChild(QtWidgets.QPushButton, 'loginButton')  # Find the button
        self.LoginButton.clicked.connect(self.printButtonPressed)  # Remember to pass the definition/method, not the return value!

        self.username = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.username.setPlaceholderText("Username")

        self.pwd = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(QtWidgets.QLineEdit.Password)

        self.secondWindow = SubjectsWindow(session)



    def printButtonPressed(self):
        print('Button Pressed ' + self.username.text() + ' ' + self.pwd.text())
        if not self.session.login(self.username.text(), self.pwd.text()):
            self.popup_error_username_password()
            return
        self.secondWindow.show()
        self.close()

        #self.close()

    def popup_error_username_password(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning!")
        msg.setText("Email o password errati")
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()
