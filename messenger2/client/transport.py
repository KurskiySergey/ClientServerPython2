import threading
from PySide2.QtCore import QObject, Signal
import socket
from messenger2.protocols.JIM import JIM
import config
import time
from messenger2.decorators import log_exception

LOCK = threading.Lock()


class ClientTransport(threading.Thread, QObject):

    new_message = Signal(str)
    alert_message = Signal(str)
    connection_lost = Signal()

    def __init__(self, ip_address, port, database, username):
        QObject.__init__(self)
        super(ClientTransport, self).__init__()

        self.database = database
        self.port = port
        self.address = ip_address
        self.username = username

        self.socket = None
        self.is_active = False
        self.connect_to_server()

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self.address, self.port))

        self.join_to_server()
        self.get_contacts()
        self.is_active = True

    def proceed_answer(self):
        protocol = self.get_answer()
        msg, send_to, send_from = protocol.get_message_info()
        print("get_answer")
        print(protocol.request.get("action"))

        if protocol.response_type:
            print("response")
            if protocol.request.get("response") == 200:
                if msg is not None:
                    print(msg)
                return True
            else:
                return False

        elif protocol.message_type:
            if send_to == self.username:
                self.database.save_msg(user=send_from, to=send_to, msg=msg)
                self.new_message.emit(send_from)

        elif protocol.get_contacts_type:
            print(send_from)
            if send_from is not None:
                print(send_from)
                self.database.add_clients(msg)
            else:
                return msg

        elif protocol.add_type:
            self.database.add_client(login=msg)

        elif protocol.del_type:
            print("delete")
            self.database.del_client(login=msg)

        elif protocol.alert_type:
            self.alert_message.emit(msg)
            return False

    def get_answer(self):
        response = self.socket.recv(config.MAX_POCKET_SIZE)
        # print(response)
        protocol = JIM(response)
        return protocol

    @log_exception(Exception)
    def send_request(self, action, **kwargs):
        print("sending request")
        try:
            with LOCK:
                print("get request")
                request = JIM().get_request(action, **kwargs)
                print(request)
                print("send request")
                self.socket.send(request)
                return self.proceed_answer()
        except Exception:
            pass

    def join_to_server(self):
        print("join")
        self.send_request(action=JIM.JOIN, user=self.username)

    def get_contacts(self):
        print("get_contacts")
        self.send_request(action=JIM.CONTACTS, send_from=self.username, user=self.username)

    def get_all_contacts(self):
        print("get_all_contacts")
        contacts = self.send_request(action=JIM.CONTACTS)
        return contacts

    def add_contact(self, username):
        print("add_contact")
        self.send_request(action=JIM.ADD, send_from=self.username, message=username, user=self.username)

    def del_contact(self, username):
        print("del_contacts")
        self.send_request(action=JIM.DELETE, send_from=self.username, message=username, user=self.username)

    def send_message(self, message, username, to):
        print("send_message")
        result = self.send_request(action=JIM.MESSAGE, send_from=username, send_to=to, message=message, user=self.username)
        if result:
            self.database.save_msg(msg=message, user=username, to=to)

    def quit(self):
        print("quit")
        self.send_request(action=JIM.QUIT, user=self.username)

    def run(self) -> None:
        print("start transport")
        while self.is_active:
            time.sleep(1)
            with LOCK:
                try:
                    self.socket.settimeout(0.5)
                    self.proceed_answer()
                except OSError:
                    self.is_active = True
                except (ConnectionAbortedError, ConnectionError, ConnectionResetError):
                    self.is_active = False
                finally:
                    self.socket.settimeout(0.5)
        print("exit")
