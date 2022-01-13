from PySide2.QtWidgets import QApplication, QMainWindow, QDialog, QAction, QLineEdit, QLabel, QVBoxLayout, QPushButton, QTableView, QHBoxLayout, QFileDialog
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt, QTimer
import sys, os
from messenger2.databases.database import ServerDatabase
import config


def start_server_gui(database):
    app = QApplication(sys.argv)
    window = ServerWindow(database=database)
    window.show()
    app.exec_()


class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super(ConfigWindow, self).__init__(parent=parent)
        self.setWindowTitle("Server Config")
        self.resize(450, 300)
        self.alert = None
        self.setUi()

    def setUi(self):
        MainVBox = QVBoxLayout()

        Vbox, self.input_database = self._create_set_line("Путь до базы данных", "Выбрать", self.open_file_dialog)
        MainVBox.addLayout(Vbox)

        Vbox, self.input_database_name = self._create_set_line("Имя базы данных")
        MainVBox.addLayout(Vbox)

        Vbox, self.input_port = self._create_set_line("Номер порта сервера")
        MainVBox.addLayout(Vbox)

        Vbox, self.input_address = self._create_set_line("Какие IP слушаем( по умолчанию все )")
        MainVBox.addLayout(Vbox)

        Vbox = QVBoxLayout()
        Hbox = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        exit_btn = QPushButton("Выйти")
        save_btn.clicked.connect(self.save_settings)
        exit_btn.clicked.connect(self.close)

        Hbox.addWidget(save_btn)
        Hbox.addWidget(exit_btn)
        Vbox.addLayout(Hbox)
        MainVBox.addLayout(Vbox)

        self.setLayout(MainVBox)

    def save_settings(self):
        settings = config.SETTINGS
        settings["server_port"] = self.input_port.text()
        settings["listen_address"] = self.input_address.text()
        settings["database_path"] = self.input_database.text()
        settings["database_file"] = self.input_database_name.text()
        with open(config.SERVER_INI, "w") as configfile:
            config.config.write(configfile)

        self.alert = InfoWindow(info_msg="настройки сохранены")
        self.alert.show()

    def open_file_dialog(self):
        file_dialog = QFileDialog(parent=self)
        file_dialog.show()

    def _create_set_line(self, text_information, button_name=None, button_action_fnc=None):
        Vbox = QVBoxLayout()
        info_label = QLabel(text=text_information)
        info_label.setAlignment(Qt.AlignCenter)
        Hbox = QHBoxLayout()
        input_line = QLineEdit()
        Hbox.addWidget(input_line)
        if button_name is not None:
            button = QPushButton(button_name)
            if button_action_fnc is not None:
                button.clicked.connect(button_action_fnc)
            Hbox.addWidget(button)

        Vbox.addWidget(info_label)
        Vbox.addLayout(Hbox)

        return Vbox, input_line

    def update_info(self):
        self.input_database.setText(config.DATABASE_PATH)
        self.input_database_name.setText(config.DATABASE_NAME)
        self.input_address.setText(config.LISTEN_ADDRESS)
        self.input_port.setText(str(config.SERVER_PORT))


class HistoryWindow(QDialog):
    def __init__(self):
        super(HistoryWindow, self).__init__()
        self.resize(450, 300)
        self.table = QTableView()
        self.alert = None
        Vbox = QVBoxLayout()
        Vbox.addWidget(self.table)
        self.setLayout(Vbox)

    def update_history_list(self, history):

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Имя", "IP", "Port", "Время входа"])

        for his in history:
            name = QStandardItem(his[1])
            ip = QStandardItem(his[0].ip_address)
            port = QStandardItem(str(his[0].port))
            log_time = QStandardItem(str(his[0].log_time))
            model.appendRow([name, ip, port, log_time])

        self.table.setModel(model)


class InfoWindow(QDialog):
    def __init__(self, info_msg):
        super(InfoWindow, self).__init__()
        self.setWindowTitle("alert")

        Vbox = QVBoxLayout()
        msg = QLabel(text=info_msg)
        msg.setAlignment(Qt.AlignCenter)
        button = QPushButton("ОК")
        button.resize(100, 20)
        button.clicked.connect(self.close)
        Vbox.addWidget(msg)
        Vbox.addWidget(button)
        self.setLayout(Vbox)


class ServerWindow(QMainWindow):

    def __init__(self, database, uic_file=None):
        super(ServerWindow, self).__init__()
        self.setWindowTitle("Server Gui")
        self.resize(700, 500)
        self.database = database
        self.alert = None
        self.config_window = ConfigWindow()
        self.history_window = HistoryWindow()
        self.setUi(uic_file)

    def setUi(self, uic_file):

        actions = []
        self.exit = QAction("Выход", self)
        self.exit.triggered.connect(self.close)
        actions.append(self.exit)

        self.update = QAction("Обновить список", self)
        self.update.triggered.connect(self.update_list)
        actions.append(self.update)

        self.history = QAction("История клиентов", self)
        self.history.triggered.connect(self.get_clients_history)
        actions.append(self.history)

        self.config = QAction("Настройки сервера", self)
        self.config.triggered.connect(self.open_config)
        actions.append(self.config)

        self._create_menu_bar(actions)
        label = QLabel(text="Список активных контактов", parent=self)
        label.move(10, 15)
        label.resize(200, 30)
        label.setAlignment(Qt.AlignCenter)
        self.table = QTableView(self)
        self.table.move(0, 40)
        self.table.resize(600, 200)
        self.update_list()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_list)
        self.timer.start(20000)

    def _setUserModel(self, users):

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Имя", "IP адресс", "Порт", "Время входа"])

        for user in users:
            login = QStandardItem(user[1].login)
            login.setEditable(False)

            ip = QStandardItem(user[0].ip_address)
            ip.setEditable(False)

            port = QStandardItem(str(user[0].port))
            port.setEditable(False)

            log_time = QStandardItem(str(user[0].log_time))
            log_time.setEditable(False)

            model.appendRow([login, ip, port, log_time])

        self.table.setModel(model)

    def _create_menu_bar(self, action_list):
        for action in action_list:
            self.menuBar().addAction(action)

    def update_list(self):
        users = self.database.get_active_user_list(join_users=True)
        self._setUserModel(users=users)

    def get_clients_history(self):
        history = self.database.get_history_list(join_users=True)
        print(history)
        self.history_window.update_history_list(history)
        self.history_window.show()

    def open_config(self):
        self.config_window.update_info()
        self.config_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = ServerDatabase(engine=config.TEST_DATABASE_ENGINE)
    db.clear_db()
    user = db.AllUsers(name="test", surname="test", login="gledstoun", password="1111")
    active_user = db.ActiveUsers(port=8888, address='127.0.0.1', user_id=1)
    history = db.UsersHistory(user_id=1, port=7777, address="localhost")
    history_2 = db.UsersHistory(user_id=1, port=7778, address="198.161.0.1")
    db.save([user, active_user, history, history_2])
    window = ServerWindow(database=db, uic_file=os.path.join(os.getcwd(), "ui\\server.ui"))
    window.show()
    user = db.AllUsers(name="test", surname="test", login="kaliter", password="1111")
    active_user = db.ActiveUsers(port=8888, address='127.0.0.1', user_id=2)
    db.save([user, active_user])
    sys.exit(app.exec_())
