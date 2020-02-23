import json

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QFileDialog
from polito_sync import PolitoWebClass
from PyQt5.QtWidgets import QMessageBox
from polito_sync import PolitoWebClass

import sys


class SubjectsWindow(QtWidgets.QMainWindow):
    def __init__(self, session):
        super(SubjectsWindow, self).__init__()
        self.session = session
        try:
            with open(".settings.json") as s:
                self.settings = json.load(s)
        except:
            print("Error: rename settings file as settings.json")

        uic.loadUi('listaMaterie.ui', self)

        #self.listWidget = QListWidget()
        self.listWidget = self.findChild(QtWidgets.QListWidget, 'listMaterie')

        # Resize width and height
        self.listWidget.resize(500, 400)

        self.listWidget.setWindowTitle('Materie')
        self.listWidget.itemClicked.connect(self.clicked)
        self.lista_materie = dict()
        self.selezionato = None

    def showMaterie(self):
        list_sub = self.session.get_subjects_list()
        print(list_sub)
        d = dict()
        i = 0
        for v in list_sub:
            self.listWidget.addItem(v[2])
            print(v[2])
            self.lista_materie[v[2]] = i
            i = i + 1
        self.show()
        print(self.lista_materie)

    def clicked(self, item):
        msg = QMessageBox()
        msg.setWindowTitle("  ")
        msg.setText("Vuoi scaricare tutto il materiale di " + item.text() + "?")
        msg.setIcon(QMessageBox.Information)
        # msg = QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        # msg.buttonClicked.OK.connect(self.scarica_materiale)
        self.selezionato = item.text()
        ret = msg.exec_()
        print(self.lista_materie[item.text()])
        if ret == QMessageBox.Ok:
            self.scarica_materiale()

    def scarica_materiale(self):

        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        file.replace("/","\\\\")

        self.session.set_download_folder(file)

        self.session.select_subject(self.lista_materie[self.selezionato])
        self.selezionato = None
        msg = QMessageBox()
        msg.setWindowTitle("  ")
        msg.setText("Materiale scaricato con successo!")
        ret = msg.exec_()
