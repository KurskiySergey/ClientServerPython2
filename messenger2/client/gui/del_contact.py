from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Signal
from PySide2.QtUiTools import QUiLoader
import config
import os


class DeleteWindow(QDialog):
    """
    Window for deleting user contacts
    """

    delete_contact = Signal(str)
    send_alert = Signal(str, str, str)

    def __init__(self, database, transport, contact):
        super(DeleteWindow, self).__init__()
        self.database = database
        self.transport = transport
        self.contact = contact
        self.alert = None
        self.send_alert.connect(self.transport.send_alert)
        self.setUI(os.path.join(config.CLIENT_UI_DIR, "del_client.ui"))

    def setUI(self, ui_file):
        """function that set up ui files"""
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()

        self.ui.user_label.setText(self.contact)
        self.ui.yes_btn.clicked.connect(self.yes)
        self.ui.no_btn.clicked.connect(self.no)

    def yes(self):
        """function that emits when client clicked yes button"""
        self.delete_contact.emit(self.contact)
        self.send_alert.emit(
            f"Пользователь {self.contact} удалил вас из контактов",
            self.contact,
            self.transport.username)
        self.close()

    def no(self):
        """close window if user decided not to delete contact"""
        self.close()

    def close(self) -> bool:
        """close window"""
        return self.ui.close()

    def show(self) -> None:
        """show gui"""
        self.ui.show()
