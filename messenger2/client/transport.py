import threading
from PySide2.QtCore import QObject, Signal, Slot
import socket
from messenger2.protocols.JIM import JIM
from messenger2 import config
import time
from messenger2.common.decorators import log_exception
from messenger2.databases.database import ClientDatabase
from messenger2.common.security.keys import get_public_key, get_client_server_public_key, save_server_public_key, generate_pair
from messenger2.common.security.encript_data import encript_server_data
from messenger2.common.security.decript_data import decript_data
from json import JSONDecodeError

LOCK = threading.Lock()


class ClientTransport(threading.Thread, QObject):

    """
    Main Transport between client and server.
    Send all requests and proceed responses
    """

    new_message = Signal(str)
    alert_message = Signal(str)
    update_contact_list = Signal()
    connection_lost = Signal()

    def __init__(self, ip_address, port, username, password):
        QObject.__init__(self)
        super(ClientTransport, self).__init__()

        self.database = None
        self.port = port
        self.address = ip_address
        self.username = username
        self.password = password
        self.socket = None
        self.is_active = False

    def connect_to_server(self):
        """
        try to make a connection with server
        If auth is wrong close socket
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self.address, self.port))

        result = self.join_to_server()
        if result:
            engine = f"{config.CLIENT_DATABASE_ENGINE}{self.username}.db3"
            self.database = ClientDatabase(engine=engine)
            self.is_active = True

    def proceed_answer(self):
        """function that proceed response from server"""
        response = self.get_answer()
        protocol = self.get_protocol_from_response(response)
        msg, send_to, send_from = protocol.get_message_info()
        print("get_answer")
        print(protocol.request.get("action"))

        if protocol.presence_type:
            print("presense")
            server_key = get_client_server_public_key(to_str=True)
            server_public_key = protocol.get_public_key()
            if server_public_key == server_key:
                print("server is equal")
            if server_key is None or server_public_key != server_key:
                print("saving server key")
                save_server_public_key(server_public_key)

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
            self.database.delete_contact_history(login=msg)

        elif protocol.alert_type:
            print("alert")
            print(protocol.get_info())
            if protocol.get_info() == "delete_contact_history":
                print(send_from)
                self.database.delete_contact_history(login=send_from)
                self.update_contact_list.emit()
            self.alert_message.emit(msg)
            return False

    def get_answer(self):
        """read data from socket"""
        response = self.socket.recv(config.MAX_POCKET_SIZE)
        # print(response)
        return response

    def get_protocol_from_response(self, response):
        """get protocol from server response"""
        try:
            protocol = JIM(request=response)
        except (UnicodeDecodeError, JSONDecodeError):
            response = decript_data(username=self.username, data=response)
            protocol = JIM(request=response)
        return protocol

    @log_exception(Exception)
    def send_request(self, request):
        """send request to server"""
        print("sending request")
        try:
            with LOCK:
                print("get request")
                # request = JIM().get_request(action, **kwargs)
                print(request)
                print("send request")
                self.socket.send(request)
                return self.proceed_answer()
        except Exception:
            print("error")

    def join_to_server(self):
        """try to join with server"""
        print("join")
        self.presence()
        request = JIM().get_request(
            action=JIM.JOIN,
            user=self.username,
            password=self.password)
        return self.send_request(request)

    def presence(self):
        """
        make presence with server
        get/send all necessary public keys
        for encrypting data
        """
        username_pk = get_public_key(username=self.username, to_str=True)
        if username_pk is None:
            generate_pair(username=self.username)
            username_pk = get_public_key(username=self.username, to_str=True)
        request = JIM().get_request(
            action=JIM.PRESENCE,
            user=self.username,
            public_key=username_pk)
        self.send_request(request)

    @Slot(str, str, str)
    def send_alert(self, msg, send_to, send_from):
        """send alert message to server"""
        print("send_alert")
        print(msg, send_to, send_from)
        request = JIM().get_request(
            action=JIM.ALERT,
            user=self.username,
            send_to=send_to,
            message=msg,
            send_from=send_from,
            info="delete_contact_history")
        print(request)
        self.send_request(request)

    def get_contacts(self):
        """send request to get user contacts"""
        print("get_contacts")
        request = JIM().get_request(
            action=JIM.CONTACTS,
            send_from=self.username,
            user=self.username)
        request = encript_server_data(request)
        self.send_request(request)

    def get_all_contacts(self):
        """send request to get all users on server"""
        print("get_all_contacts")
        request = JIM().get_request(action=JIM.CONTACTS, user=self.username)
        request = encript_server_data(request)
        contacts = self.send_request(request)
        return contacts

    def add_contact(self, username):
        """send request to add new contact to user list"""
        print("add_contact")
        request = JIM().get_request(
            action=JIM.ADD,
            send_from=self.username,
            message=username,
            user=self.username)
        request = encript_server_data(request)
        self.send_request(request)

    def del_contact(self, username):
        """send request to del contact from user list"""
        print("del_contacts")
        request = JIM().get_request(
            action=JIM.DELETE,
            send_from=self.username,
            message=username,
            user=self.username)
        self.send_request(request)

    def send_message(self, message, username, to):
        """send message to another user"""
        print("send_message")
        request = JIM().get_request(
            action=JIM.MESSAGE,
            send_from=username,
            send_to=to,
            message=message,
            user=self.username)
        request = encript_server_data(request)
        result = self.send_request(request)
        if result:
            self.database.save_msg(msg=message, user=username, to=to)

    def quit(self):
        """send request that client is closed or quit"""
        print("quit")
        request = JIM().get_request(action=JIM.QUIT, user=self.username)
        request = encript_server_data(request)
        self.send_request(request)

    def run(self) -> None:
        """start main transport event"""
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
