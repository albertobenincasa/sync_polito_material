from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from polito_sync import PolitoWebClass
from PyQt5.QtWidgets import QMessageBox
from subjects_window import SubjectsWindow

import json

import sys


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self, session):
        super(LoginWindow, self).__init__()
        self.session = session
        try:
            with open("settings.json") as s:
                self.settings = json.load(s)
        except:
            print("Error: rename settings file as settings.json")

        uic.loadUi('loginUI.ui', self)

        #self.setGeometry(500,500,500,500)

        self.LoginButton = self.findChild(QtWidgets.QPushButton, 'loginButton')  # Find the button
        self.LoginButton.clicked.connect(
            self.login_button_pressed)  # Remember to pass the definition/method, not the return value!

        self.username = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.username.setPlaceholderText("Username")

        self.pwd = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(QtWidgets.QLineEdit.Password)

        self.checkBox = self.findChild(QtWidgets.QCheckBox, 'checkBox')
        self.checkBox.setCheckState(0)

        self.secondWindow = SubjectsWindow(session)

        #enabled = 1   not enalbled = 0
        if self.settings['credentials']['enabled']:
            print(self.settings['credentials']['enabled'])
            us = QtWidgets.QLineEdit
            self.username.setText(self.settings['credentials']['username'])
            self.pwd.setText(self.settings['credentials']['password'])
            self.checkBox.setCheckState(2)

    def login_button_pressed(self):
        print('Button Pressed ' + self.username.text() + ' ' + self.pwd.text())
        if not self.session.login(self.username.text(), self.pwd.text()):
            self.popup_error_username_password()
            return
        if self.checkBox.isChecked():
            self.save_credentials(self.username.text(), self.pwd.text())
        else:
            self.delete_credentials()
        self.secondWindow.showMaterie()
        self.close()

        # self.close()

    def save_credentials(self, username, pwd):
        self.settings['credentials']['username'] = username
        self.settings['credentials']['password'] = pwd
        self.settings['credentials']['enabled'] = 1
        # self.s.write(self.settings)
        print(self.settings)
        # self.settings.write()
        with open("settings.json", 'w') as s:
            json.dump(self.settings, s)

    def delete_credentials(self):
        self.settings['credentials']['username'] = None
        self.settings['credentials']['password'] = None
        self.settings['credentials']['enabled'] = 0
        with open("settings.json", 'w') as s:
            json.dump(self.settings, s)

    def popup_error_username_password(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning!")
        msg.setText("Email o password errati")
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()
