from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Slot
from PySide2.QtUiTools import QUiLoader
import config
import os
from messenger2.client.gui.alert_window import AlertWindow
from messenger2.client.gui.client_window import ClientWindow
from messenger2.client.transport import ClientTransport
from messenger2.common.security.hash_password import get_hash_from_password


class WelcomeWindow(QDialog):

    def __init__(self, ip_address, port, username=None, password=None):
        super(WelcomeWindow, self).__init__()
        self.database = None
        self.transport = None
        self.ip_address = ip_address
        self.port = port
        self.alert = None
        self.ui = None
        self.username = username
        self.password = password
        self.setUI(os.path.join(config.CLIENT_UI_DIR, "welcome.ui"))

    def setUI(self, ui_file):
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()

        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.enter_btn.clicked.connect(self.register_user)

    def register_user(self):
        username = self.ui.user_edit.text()
        password = get_hash_from_password(password=self.ui.pwd_edit.text(), salt=username)

        self.transport = ClientTransport(ip_address=self.ip_address, port=self.port,
                                         username=username, password=password)
        self.transport.alert_message.connect(self.show_alert)
        self.transport.connect_to_server()
        if self.transport.is_active:
            self.database = self.transport.database
            self.transport.setDaemon(True)
            self.transport.start()
            window = ClientWindow(database=self.database, transport=self.transport, username=username,
                                  ui_file=os.path.join(config.CLIENT_UI_DIR, "client.ui"))
            window.show()
            self.close()
        else:
            self.transport = None
            pass
            # self.alert = AlertWindow(info_msg="Неверный логин или пароль")
            # self.alert.show()

    @Slot(str)
    def show_alert(self, msg):
        self.alert = AlertWindow(info_msg=msg)
        self.alert.show()

    def close(self) -> bool:
        return self.ui.close()

    def show(self) -> None:
        if self.username is not None and self.password is not None:
            self.ui.show()
            self.ui.user_edit.setText(self.username)
            self.ui.pwd_edit.setText(self.password)
            self.register_user()
        else:
            self.ui.show()