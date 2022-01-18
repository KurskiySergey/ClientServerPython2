from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PySide2.QtCore import Qt, QFile, Slot, QEvent
from PySide2.QtUiTools import QUiLoader
import sys
from messenger2.databases.database import ClientDatabase
import config
from messenger2.client.transport import ClientTransport
from messenger2.client.gui.add_contact import AddWindow
from messenger2.client.gui.alert_window import AlertWindow
from messenger2.client.gui.del_contact import DeleteWindow
from messenger2.client.gui.open_dialog import OpenWindow


class ClientWindow(QMainWindow):
    def __init__(self, database, transport, ui_file, username="user"):
        super(ClientWindow, self).__init__()
        self.ui = None
        self.username = username
        self.transport = transport
        self.active_contact = None
        self.database = database
        self.add_window = None
        self.del_window = None
        self.open_dialog = None
        self.alert = None
        self.setUI(ui_file)

        self.transport.alert_message.connect(self.alert_msg)
        self.transport.new_message.connect(self.new_msg)
        self.transport.update_contact_list.connect(self.show_contact_history)
        self.transport.get_contacts()
        self.get_contact_list()

    def setUI(self, ui_file):
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()

        self.ui.menu_exit.triggered.connect(self.close)

        self.ui.add_contact_btn.clicked.connect(self.open_add_window)
        self.ui.menu_add_contact.triggered.connect(self.open_add_window)

        self.ui.del_contact_btn.clicked.connect(self.open_del_window)
        self.ui.menu_del_contact.triggered.connect(self.open_del_window)

        self.ui.send_btn.clicked.connect(self.send_msg)
        self.ui.clear_msg_btn.clicked.connect(self.clear_msg)

        self.ui.contact_list.doubleClicked.connect(
            lambda: self.show_contact_history())
        self.ui.history_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.ui.history_list.setWordWrap(True)

        self.ui.installEventFilter(self)

    def open_add_window(self):
        self.add_window = AddWindow(
            database=self.database,
            transport=self.transport)
        self.add_window.add_contact.connect(self.add_contact)
        self.add_window.show()
        print("add contact")

        pass

    def open_del_window(self):
        if self.active_contact is not None:
            self.del_window = DeleteWindow(
                database=self.database,
                transport=self.transport,
                contact=self.active_contact)
            self.del_window.delete_contact.connect(self.del_contact)
            self.del_window.show()
            print("del contact")
        else:
            self.alert = AlertWindow(info_msg="Выберите контакт для удаления")
            self.alert.show()
        pass

    def open_dialog_window(self, new_contact):
        if self.database.check_contact(new_contact):
            self.open_dialog = OpenWindow(
                database=self.database,
                transport=self.transport,
                contact=new_contact,
                is_new=False)
        else:
            self.open_dialog = OpenWindow(
                database=self.database,
                transport=self.transport,
                contact=new_contact,
                is_new=True)

        self.open_dialog.add_contact.connect(self.add_contact)
        self.open_dialog.select_history.connect(self.show_contact_history)
        self.open_dialog.show()

    def send_msg(self):
        print("send msg")
        if self.active_contact is not None:
            msg = self.ui.msg_window.toPlainText()
            self.transport.send_message(
                message=msg,
                username=self.username,
                to=self.active_contact)
            self.show_contact_history()
            self.clear_msg()
        else:
            self.clear_msg()
            self.alert = AlertWindow(info_msg="Не выбран диалог")
            self.alert.show()
        pass

    @Slot(str)
    def alert_msg(self, msg):
        print("alert signal")
        self.alert = AlertWindow(info_msg=msg)
        self.alert.show()

    def clear_msg(self):
        print("clear_msg")
        self.ui.msg_window.setText("")
        pass

    def show(self) -> None:
        self.ui.show()

    @Slot(str)
    def add_contact(self, contact):
        try:
            self.transport.add_contact(contact)
        except Exception:
            self.alert = AlertWindow(
                info_msg="Не удалось добавить пользователя")

        finally:
            self.get_contact_list()

    @Slot(str)
    def del_contact(self, contact):
        try:
            self.transport.del_contact(contact)
            self.show_contact_history(contact="")
        except Exception:
            self.alert = AlertWindow(
                info_msg="Не удалось удалить пользователя")

        finally:
            self.get_contact_list()

    def get_contact_list(self):
        contact_list = self.database.get_contacts()
        print(contact_list)
        model = QStandardItemModel()
        for contact in contact_list:
            if contact.login != "":
                list_contact = QStandardItem(contact.login)
                list_contact.setEditable(False)
                model.appendRow(list_contact)

        self.ui.contact_list.setModel(model)

    @Slot()
    def show_contact_history(self, contact=None):
        if contact is None:
            login = self.ui.contact_list.currentIndex().data()
            print(login)
            self.active_contact = login
        else:
            self.active_contact = contact
        print(self.active_contact)
        history_list = self.database.get_contact_history(
            login=self.active_contact)

        model = QStandardItemModel()

        for history in history_list:
            msg = QStandardItem(
                f"{history.user} -> {history.msg} : {history.when}")

            if history.user == self.active_contact:
                msg.setTextAlignment(Qt.AlignRight)
                msg.setBackground(QBrush(QColor("red")))
            else:
                msg.setTextAlignment(Qt.AlignLeft)
                msg.setBackground(QBrush(QColor("green")))
            msg.setEditable(False)
            model.appendRow(msg)

        self.ui.history_list.setModel(model)

    def new_msg(self, send_from):
        if self.active_contact == send_from:
            self.show_contact_history()
        else:
            self.open_dialog_window(new_contact=send_from)

    def closeEvent(self, event) -> None:
        self.transport.quit()
        QApplication.exit()

    def eventFilter(self, obj, event) -> bool:
        if obj is self.ui:
            if event.type() == QEvent.Close:
                self.transport.quit()
                event.accept()
                return True

        return False


if __name__ == "__main__":
    app = QApplication()
    test_db = ClientDatabase(engine=config.TEST_DATABASE_ENGINE)
    transport = ClientTransport(
        ip_address=config.USER_ADDRESS,
        port=config.USER_PORT,
        database=test_db,
        username="user")
    transport.setDaemon(True)
    transport.start()
    window = ClientWindow(database=test_db, transport=transport)
    window.show()
    sys.exit(app.exec_())
