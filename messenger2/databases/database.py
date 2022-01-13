from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from config import TEST_DATABASE_ENGINE


class ServerDatabase:
    Base = declarative_base()

    class AllUsers(Base):
        __tablename__ = "all_users"
        id = Column(Integer, primary_key=True)
        name = Column(String, default="")
        surname = Column(String, default="")
        login = Column(String, default="", unique=True)
        password = Column(String)
        last_login = Column(DateTime, default=datetime.datetime.now())

        def __init__(self, name, surname, login, password):
            self.name = name
            self.surname = surname
            self.login = login
            self.password = password
            self.last_login = datetime.datetime.now()

        def __repr__(self):
            return f"<AllUsers({self.name}, {self.surname}, {self.login}, {self.password})>"

    class UserContacts(Base):
        __tablename__ = "contacts"
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey("all_users.id"))
        contact = Column(Integer, ForeignKey("all_users.id"))

        def __init__(self, user, contact):
            self.user = user
            self.contact = contact

        def __repr__(self):
            return f"<UserContacts({self.user}, {self.contact})>"

    class ActiveUsers(Base):
        __tablename__ = "active_users"
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('all_users.id'))
        port = Column(Integer, default=122)
        ip_address = Column(String)
        log_time = Column(DateTime, default=datetime.datetime.now())

        def __init__(self, user_id, port, address):
            self.user_id = user_id
            self.port = port
            self.ip_address = address
            self.log_time = datetime.datetime.now()

        def __repr__(self):
            return f"<ActiveUsers({self.user_id}, {self.port}, {self.ip_address}, {self.log_time})>"

    class UsersHistory(Base):
        __tablename__ = "users_history"
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('all_users.id'))
        port = Column(Integer)
        ip_address = Column(String)
        log_time = Column(DateTime, default=datetime.datetime.now())

        def __init__(self, user_id, port, address):
            self.user_id = user_id
            self.port = port
            self.ip_address = address
            self.log_time = datetime.datetime.now()

        def __repr__(self):
            return f"<UsersHistory({self.user_id}, {self.port}, {self.ip_address}, {self.log_time})>"

    def __init__(self, engine):
        self._engine = create_engine(engine)
        self.Base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)

    @property
    def session(self):
        return self._session()

    def save(self, info:list ):
        session = self.session
        for data in info:
            session.add(data)

        session.commit()
        session.close()

    def get_user(self, login):
        session = self.session
        user = session.query(self.AllUsers).filter_by(login=login).first()
        session.close()
        return user

    def delete_active_user(self, login):
        session = self.session
        user_id = session.query(self.AllUsers).filter_by(login=login).first().id
        session.query(self.ActiveUsers).filter_by(user_id=user_id).delete()
        session.commit()
        session.close()

    def clear_active_users(self):
        session = self.session
        session.query(self.ActiveUsers).delete()
        session.commit()
        session.close()

    def delete(self, query):
        session = self.session
        query.delete()
        session.commit()
        session.close()

    def update(self):
        pass

    def get_user_list(self):
        session = self.session
        users = session.query(self.AllUsers).all()
        session.close()
        return users

    def get_contacts(self, username):
        session = self.session
        contacts = session.query(self.AllUsers.login).all()
        session.close()
        return [contact[0] if contact[0] != username else '' for contact in contacts]

    def get_user_contacts(self, username):
        session = self.session
        user = session.query(self.AllUsers.id).filter_by(login=username).first()

        user_contacts = session.query(self.UserContacts, self.AllUsers).filter_by(user=user.id)\
            .join(self.AllUsers, self.UserContacts.contact == self.AllUsers.id).all()

        return [user[1].login for user in user_contacts]

    def get_history_list(self, join_users=False):
        session = self.session
        if join_users:
            history = session.query(self.UsersHistory, self.AllUsers.login).join(self.AllUsers, self.AllUsers.id==self.UsersHistory.user_id).all()
        else:
            history = session.query(self.UsersHistory).all()
        session.close()
        return history

    def get_active_user_list(self, join_users=False):
        session = self.session
        if join_users:
            active_users = session.query(self.ActiveUsers, self.AllUsers).join(self.AllUsers, self.AllUsers.id==self.ActiveUsers.user_id).all()
        else:
            active_users = session.query(self.ActiveUsers).all()
        session.close()
        return active_users

    def clear_db(self):
        session = self.session
        session.query(self.AllUsers).delete()
        session.query(self.UsersHistory).delete()
        session.query(self.ActiveUsers).delete()
        session.query(self.UserContacts).delete()
        session.commit()
        session.close()

    def add_contact(self, username, login):
        session = self.session
        user = session.query(self.AllUsers).filter_by(login=username)
        contact = session.query(self.AllUsers).filter_by(login=login)
        if user.count() != 0 and contact.count() != 0:
            if session.query(self.UserContacts).filter_by(user=user.first().id, contact=contact.first().id).count() == 0:
                # add contact
                contact = self.UserContacts(user=user.first().id, contact=contact.first().id)
                session.add(contact)
                session.commit()
                session.close()
                return True
        session.close()
        return False

    def del_contact(self, username, login):
        session = self.session
        user = session.query(self.AllUsers).filter_by(login=username)
        contact = session.query(self.AllUsers).filter_by(login=login)
        print(user.first())
        print(user.first())
        if user.count() != 0 and contact.count() != 0:
            contact_to_del = session.query(self.UserContacts).filter_by(user=user.first().id, contact=contact.first().id)
            if contact_to_del.count() != 0:
                # delete contact
                contact_to_del.delete()
                session.commit()
                session.close()
                return True
        session.close()
        return False


class ClientDatabase:

    Base = declarative_base()

    class Contacts(Base):
        __tablename__ = "contacts"
        id = Column(Integer, primary_key=True)
        login = Column(String)

        def __init__(self, login):
            self.login = login

        def __repr__(self):
            return f"<Contacts({self.login})"

    class HistoryMessage(Base):
        __tablename__ = "history"
        id = Column(Integer, primary_key=True)
        user = Column(String)
        to = Column(String)
        msg = Column(String)
        when = Column(DateTime, default=datetime.datetime.now())

        def __init__(self, msg, user, to):
            self.msg = msg
            self.user = user
            self.to = to
            self.when = datetime.datetime.now()

        def __repr__(self):
            return f"<History({self.user}, {self.to}, {self.msg}, {self.when})>"

    @property
    def session(self):
        return self._session()

    def __init__(self, engine):
        self._engine = create_engine(engine)
        self.Base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)

    def save_msg(self, user, to, msg):
        log = self.HistoryMessage(msg=msg, user=user, to=to)
        session = self.session
        session.add(log)
        session.commit()
        session.close()

    def check_contact(self, login):
        session = self.session
        client = session.query(self.Contacts).filter_by(login=login)
        session.close()
        if client.count() == 0:
            return False
        return True

    def add_client(self, login):
        session = self.session
        client = self.Contacts(login=login)
        session.add(client)
        session.commit()
        session.close()

    def del_client(self, login):
        session = self.session
        client = session.query(self.Contacts).filter_by(login=login)
        client.delete()
        session.commit()
        session.close()

    def add_clients(self, logins: list):
        session = self.session
        session.query(self.Contacts).delete()
        for login in logins:
            client = self.Contacts(login=login)
            session.add(client)
        session.commit()
        session.close()

    def get_contacts(self):
        session = self.session
        contacts = session.query(self.Contacts).all()
        session.close()
        return contacts

    def get_contact_history(self, login):
        session = self.session
        history = session.query(self.HistoryMessage).filter(or_(self.HistoryMessage.user==login, self.HistoryMessage.to==login)).order_by(self.HistoryMessage.when).all()
        session.close()
        return history

    def create_user(self, name, surname, login, password):
        pass

    def clear_db(self):
        session = self.session
        session.query(self.Contacts).delete()
        session.query(self.HistoryMessage).delete()
        session.commit()
        session.close()


if __name__ == "__main__":
    info = []
    db = ServerDatabase(engine=TEST_DATABASE_ENGINE)
    session = db.session
    test_query = session.query(db.AllUsers)
    db.delete(test_query)
    user = db.AllUsers(name="test", surname="test", login="test_1", password='1111')
    find_query = db.session.query(db.AllUsers).filter_by(login="test_1")
    if find_query.count() == 0:
        info.append(user)
        db.save(info)
        info = []
        find_query = db.session.query(db.AllUsers).filter_by(login="test_1")
    active_user = db.ActiveUsers(user_id=find_query.first().id, port=100, address="localhost")
    info.append(active_user)
    db.save(info)
    users = db.get_user_list()
    print(users)
    print(users[0].login)
    db.clear_db()


