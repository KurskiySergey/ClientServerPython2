from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Signal
from PySide2.QtUiTools import QUiLoader
import config
import os


class OpenWindow(QDialog):

    add_contact = Signal(str)
    select_history = Signal(str)

    def __init__(self, database, transport, contact, is_new):
        super(OpenWindow, self).__init__()
        self.database = database
        self.transport = transport
        self.contact = contact
        self.is_new = is_new
        self.alert = None
        self.setUI(os.path.join(config.CLIENT_UI_DIR, "open_dialog.ui"))

    def setUI(self, ui_file):
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()
        if not self.is_new:
            self.ui.info_label.setText(f"Получено сообщение от {self.contact}\nОткрыть диалог ?")
        else:
            self.ui.info_label.setText(f"Получено сообщение от нового пользователя {self.contact}\n"
                                       f"Добавить его в контакты и открыть диалог ?")
        self.ui.yes_btn.clicked.connect(self.yes)
        self.ui.no_btn.clicked.connect(self.no)

    def yes(self):
        if self.is_new:
            self.add_contact.emit(self.contact)
        self.select_history.emit(self.contact)
        self.close()

    def no(self):
        self.close()

    def close(self) -> bool:
        return self.ui.close()

    def show(self) -> None:
        self.ui.show()