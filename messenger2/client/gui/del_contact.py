from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Signal
from PySide2.QtUiTools import QUiLoader
import config
import os


class DeleteWindow(QDialog):

    delete_contact = Signal(str)

    def __init__(self, database, transport, contact):
        super(DeleteWindow, self).__init__()
        self.database = database
        self.transport = transport
        self.contact = contact
        self.alert = None
        self.setUI(os.path.join(config.CLIENT_UI_DIR, "del_client.ui"))

    def setUI(self, ui_file):
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()

        self.ui.user_label.setText(self.contact)
        self.ui.yes_btn.clicked.connect(self.yes)
        self.ui.no_btn.clicked.connect(self.no)

    def yes(self):
        self.delete_contact.emit(self.contact)
        self.close()

    def no(self):
        self.close()

    def close(self) -> bool:
        return self.ui.close()

    def show(self) -> None:
        self.ui.show()