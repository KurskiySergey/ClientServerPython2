from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Signal
from PySide2.QtUiTools import QUiLoader
import config
import os


class OpenWindow(QDialog):

    """
    Window that helps users to open new dialog
    or open existing if some contact sent new message
    """

    add_contact = Signal(str)
    select_history = Signal(str)
    send_alert = Signal(str, str, str)

    def __init__(self, database, transport, contact, is_new):
        super(OpenWindow, self).__init__()
        self.database = database
        self.transport = transport
        self.contact = contact
        self.is_new = is_new
        self.alert = None
        self.send_alert.connect(self.transport.send_alert)
        self.setUI(os.path.join(config.CLIENT_UI_DIR, "open_dialog.ui"))

    def setUI(self, ui_file):
        """function that set up ui files"""
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()
        if not self.is_new:
            self.ui.info_label.setText(
                f"Получено сообщение от {self.contact}\nОткрыть диалог ?")
        else:
            self.ui.info_label.setText(
                f"Получено сообщение от нового пользователя {self.contact}\n"
                f"Добавить его в контакты и открыть диалог ?")
        self.ui.yes_btn.clicked.connect(self.yes)
        self.ui.no_btn.clicked.connect(self.no)

    def yes(self):
        """function that emits if user clicked yes button"""
        if self.is_new:
            self.add_contact.emit(self.contact)
        self.select_history.emit(self.contact)
        self.close()

    def no(self):
        """function that emits if user clicked no button"""
        if self.is_new:
            self.send_alert.emit(
                "Пользователь отказался добавить вас в контакты",
                self.contact,
                self.transport.username)
        self.close()

    def close(self) -> bool:
        """close window"""
        return self.ui.close()

    def show(self) -> None:
        """show gui"""
        self.ui.show()
