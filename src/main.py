from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from polito_sync import PolitoWebClass
from PyQt5.QtWidgets import QMessageBox

import sys
import json
from login_window import LoginWindow

# def window():
#     app = QApplication(sys.argv)
#     win = QMainWindow()
#     win.setGeometry(1000, 200, 300, 300)  # (x,y,w,h) --> where start(x,y) how big(w,h)
#     win.setWindowTitle("Polito Sync Material")
#
#     label = QtWidgets.QLabel(win)
#     label.setText("label")
#     label.move(50, 50)
#
#     win.show()
#     sys.exit(app.exec_())
#
if __name__ == "__main__":
    session = PolitoWebClass()
    try:
        with open(".settings.json") as s:
            settings = json.load(s)
    except:
        #json doesn' t exist
        #print("Error: rename settings file as settings.json")
        with open(".settings.json","w") as s:
            dict_json = {"download_folder": "", "credentials": {"enabled": 0, "username": "", "password": ""}}
            new_json = json.dump(dict_json,s,ensure_ascii=False, indent=4)
            print(new_json)

    print(settings)
    #settings = json.load(s)
    #session.set_download_folder(settings['download_folder'])
    session.set_file_name('web')
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow(session)
    window.show()

    sys.exit(app.exec_())
