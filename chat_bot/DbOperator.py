import sqlite3


class DbOperator():
    @staticmethod
    def connect(db_address):
        connect = sqlite3.connect(db_address, check_same_thread=False)
        return connect

    @staticmethod
    def get_cursor(connect):
        cursor = connect.cursor()
        return cursor

    @staticmethod
    def create(connection):
        connection.execute('CREATE TABLE sessions (chat, language)')

    @staticmethod
    def select(cursor, chat_id):
        cursor.execute("SELECT * FROM sessions WHERE chat='{0}'".format(chat_id))
        row = cursor.fetchone()
        return row

    @staticmethod
    def insert(cursor, chat_id, language):
        cursor.execute("INSERT INTO sessions (chat,language) VALUES ('{0}','{1}')".format(chat_id, language))
        return cursor

    @staticmethod
    def update(cursor, chat_id, language):
        cursor.execute("UPDATE sessions SET language = '{0}' WHERE chat = '{1}'".format(language, chat_id))
        return cursor

    @staticmethod
    def disconnect(connect):
        connect.commit()
        connect.close()