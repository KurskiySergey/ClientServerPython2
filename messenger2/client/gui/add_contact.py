from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Signal
from PySide2.QtUiTools import QUiLoader
import os
import config
from messenger2.client.gui.alert_window import AlertWindow


class AddWindow(QDialog):

    add_contact = Signal(str)

    def __init__(self, database, transport):
        super(AddWindow, self).__init__()
        self.database = database
        self.transport = transport
        self.alert = None
        self.setUI(os.path.join(config.CLIENT_UI_DIR, "add_client.ui"))
        self.update_list()

    def setUI(self, ui_file):
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()

        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.choose_btn.clicked.connect(self.choose_contact)
        self.ui.update_btn.clicked.connect(self.update_list)

    def update_list(self):
        self.ui.selector.clear()
        users = self.transport.get_all_contacts()
        users.remove(self.transport.username)
        contacts = [contact.login for contact in self.database.get_contacts()]
        available_contacts = set(users) - set(contacts)

        if len(available_contacts) == 0:
            self.alert = AlertWindow(info_msg="Нет доступных контактов")
            self.alert.show()
        else:
            self.ui.selector.addItems(available_contacts)

    def choose_contact(self):
        contact = self.ui.selector.currentText()
        self.add_contact.emit(contact)
        self.update_list()

    def show(self) -> None:
        self.ui.show()

    def close(self) -> bool:
        return self.ui.close()