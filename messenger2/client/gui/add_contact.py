from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Signal
from PySide2.QtUiTools import QUiLoader
import os
from messenger2 import config
from messenger2.client.gui.alert_window import AlertWindow


class AddWindow(QDialog):
    """
    Window for helping clients add new contacts
    """

    add_contact = Signal(str)

    def __init__(self, database, transport):
        super(AddWindow, self).__init__()
        self.database = database
        self.transport = transport
        self.alert = None
        self.setUI(os.path.join(config.CLIENT_UI_DIR, "add_client.ui"))
        self.update_list()

    def setUI(self, ui_file):
        """function that set up ui files"""
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()

        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.choose_btn.clicked.connect(self.choose_contact)
        self.ui.update_btn.clicked.connect(self.update_list)

    def update_list(self):
        """function that update users list"""
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
        """function that activates when client choose user to add"""
        contact = self.ui.selector.currentText()
        self.add_contact.emit(contact)
        self.update_list()

    def show(self) -> None:
        """show gui"""
        self.ui.show()

    def close(self) -> bool:
        """close window"""
        return self.ui.close()