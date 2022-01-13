from select import select
from socket import socket, AF_INET, SOCK_STREAM
import config
from messenger2.databases.database import ServerDatabase
import logging
from messenger2.protocols.JIM import JIM
from messenger2.logs.log_configs import server_log_config
from messenger2.decorators import log_exception
import messenger2.descriptors as desc
from messenger2.metaclasses import ServerVerifier
import argparse
import threading
from messenger2.gui.server_gui import start_server_gui


class Server(threading.Thread, metaclass=ServerVerifier):
    port = desc.Port()
    address = desc.Address()

    def __init__(self, address=None, port=None):
        super(Server, self).__init__()
        self.server_logger = logging.getLogger(server_log_config.SERVER_LOGGER)
        self.db = ServerDatabase(engine=config.DATABASE_ENGINE)

        self.db.clear_active_users()

        self.server_logger.info('Получение адреса и порта')
        if address is None or port is None:
            self.address, self.port = self.get_parameters(address=address, port=port)
        else:
            self.address = address
            self.port = port

        self.server = None

        self.clients = []
        self.messages = []
        self.client_names = {}

    @log_exception(Exception)
    def get_parameters(self, address=None, port=None):

        parser = argparse.ArgumentParser(description="server parser")
        parser.add_argument("-p", "--port", type=int, default=config.SERVER_PORT, help="port name")
        parser.add_argument("-a", "--address", type=str, default=config.LISTEN_ADDRESS, help="address name")
        args = parser.parse_args()

        if address is None:
            address_param = args.address
        else:
            address_param = address

        if port is None:
            port_param = args.port
        else:
            port_param = port

        return address_param, port_param

    @log_exception(Exception)
    def get_socket(self):

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.address, self.port))
        server_socket.settimeout(0.2)
        server_socket.listen(config.MAX_CONNECTIONS)
        print('Start server')
        return server_socket

    @log_exception(Exception)
    def start_server(self):
        self.server_logger.info('Запуск сервера')
        self.server = self.get_socket()
        self.server_logger.info('Запуск ожидания клиентов')
        # self.gui_thread = start_server_gui(database=self.db)
        print("start event listener")
        self.event_listener()

    @log_exception(Exception)
    def event_listener(self):
        while True:

            try:
                client_socket, addr = self.server.accept()
            except Exception:
                pass
            else:
                self.server_logger.info(f'Получили данные от клиента с адресом {addr}')
                self.clients.append(client_socket)
                # print(self.clients)

            finally:
                recv_data_lst = []
                send_data_lst = []
                error_list = []

                if self.clients:
                    recv_data_lst, send_data_lst, error_list = select(self.clients, self.clients, [], 0)

                if recv_data_lst:
                    self.server_logger.info(f'recv_data_lst = {len(recv_data_lst)}')
                    for client in recv_data_lst:
                        try:
                            self.proceed_response(client=client, addr=addr)
                        except Exception:
                            self.server_logger.debug(f'Пользователь {client.getpeername()} отключился')
                            self.clients.remove(client)

                for message in self.messages:
                    print(f"sending message {message}")
                    to = message.get("to")
                    sender = message.get("from")
                    msg = message.get("msg")
                    print(self.client_names)
                    client_to = self.client_names.get(to)
                    client_from = self.client_names.get(sender)
                    if client_to is not None:
                        response = JIM().get_request(action=JIM.MESSAGE, message=msg, send_to=to, send_from=sender)
                        self.send_response(client=client_to, response=response)
                    else:
                        print("error")
                        response = JIM().get_request(action=JIM.ALERT, message="user is not online")
                        self.send_response(client=client_from, response=response)

                self.messages.clear()

    @log_exception(Exception)
    def get_protocol_from_client_request(self, client):
        print("get protocol")
        client_request = client.recv(config.MAX_POCKET_SIZE)
        protocol = JIM(request=client_request)
        return protocol

    @log_exception(Exception)
    def proceed_response(self, client, addr):
        self.server_logger.info(f'Получили данные от клиента {client.getpeername()}')
        protocol = self.get_protocol_from_client_request(client=client)

        self.server_logger.info('Обработка клиентского запроса')
        response = self.proceed_event(protocol=protocol, addr=addr, client=client)
        self.send_response(client=client, response=response)

    @log_exception(Exception)
    def send_response(self, client, response):
        client.send(response)

    @log_exception(Exception)
    def proceed_event(self, protocol, addr, client):
        print(protocol)
        username = protocol.get_user()
        msg, send_to, send_from = protocol.get_message_info()
        print(f"get username = {username}")
        if protocol.message_type:
            print("procced message")
            print(msg)
            self.messages.append({"msg": msg, "from": send_from, "to": send_to})
            if self.client_names.get(send_to) is None:
                protocol.set_response_code(404)
            else:
                protocol.set_message("message sent")

        if protocol.join_type:
            print("trying to join...")
            if username is not None:
                self.client_names[username] = client
                db_info = []
                db_user = self.db.get_user(login=username)
                if db_user is None:
                    self.db.save([self.db.AllUsers(name="", surname="", login=username, password="1111")])
                    db_user = self.db.get_user(login=username)
                active_user = self.db.ActiveUsers(user_id=db_user.id, port=addr[1], address=addr[0])
                history = self.db.UsersHistory(user_id=db_user.id, port=addr[1], address=addr[0])
                db_info.append(active_user)
                db_info.append(history)
                self.db.save(db_info)
                protocol.set_message("Вы подключились к серверу")

            else:
                self.server_logger.error(f'Ошибка {402} : {protocol.SERVER_CODES.get(402)}')
                protocol.set_response_code(402)

        if protocol.quit_type:
            if username is not None:
                print(self.client_names)
                print(self.clients)
                self.clients.remove(self.client_names[username])
                self.client_names.pop(username)
                self.db.delete_active_user(username)
            else:
                self.server_logger.error(f'Ошибка {401} : {protocol.SERVER_CODES.get(401)}')
                # Server.CHAT_MSG.append(' ')
                protocol.set_response_code(401)

            protocol.set_message(message='Вы отключились от сервера')

        if protocol.presence_type:
            if username is not None:
                protocol.set_message(message='test ping')
            else:
                self.server_logger.error(f'Ошибка {402} : {protocol.SERVER_CODES.get(402)}')
                protocol.set_response_code(402)

        if protocol.get_contacts_type:
            if send_from is not None:
                contacts = self.db.get_user_contacts(send_from)
                protocol.set_message(message=contacts, send_from=send_from)
            else:
                contacts = self.db.get_contacts(username)
                protocol.set_message(message=contacts)
            print(contacts)
            protocol.set_response_action(JIM.CONTACTS)

        # else:
        #     self.server_logger.error(f'Ошибка {402} : {protocol.SERVER_CODES.get(402)}')
        #     # Server.CHAT_MSG.append(' ')
        #     protocol.set_response_code(402)

        if protocol.add_type:
            print("add")
            if username is not None:
                msg, send_to, send_from = protocol.get_message_info()
                result = self.db.add_contact(username, msg)
                if result:
                    protocol.set_message(message=f"{msg}")
                    protocol.set_info(info=f"add {msg}")
                    protocol.set_response_action(action=JIM.ADD)
                else:
                    protocol.set_response_code(404)

            else:
                self.server_logger.error(f'Ошибка {402} : {protocol.SERVER_CODES.get(402)}')
                # Server.CHAT_MSG.append(' ')
                protocol.set_response_code(402)

        if protocol.del_type:
            if username is not None:
                msg, send_to, send_from = protocol.get_message_info()
                result = self.db.del_contact(username, msg)
                if result:
                    protocol.set_message(message=f"{msg}")
                    protocol.set_info(info=f"del {msg}")
                    protocol.set_response_action(action=JIM.DELETE)
                else:
                    protocol.set_response_code(404)
            else:
                self.server_logger.error(f'Ошибка {402} : {protocol.SERVER_CODES.get(402)}')
                # Server.CHAT_MSG.append(' ')
                protocol.set_response_code(402)

        return protocol.get_response()

    def run(self) -> None:
        self.start_server()


if __name__ == "__main__":
    server = Server()
    server.daemon = True
    server.start()
    start_server_gui(database=server.db)

