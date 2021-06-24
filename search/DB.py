from .Config import BaseConfig
import sqlite3
import re

class DB:
    #region create tables sql lines
    drop_tables = [
        "DROP TABLE IF EXISTS dhcp2rad;",
        "DROP TABLE IF EXISTS main;",
        "DROP TABLE IF EXISTS dhcp;",
        "DROP TABLE IF EXISTS ip;",
    ]
    create_tables = [
        """
            CREATE TABLE ip (
            ip TEXT NOT NULL,
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
        );
        """,
        """
            CREATE TABLE main (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            ip_id INTEGER NOT NULL,
            context TEXT,
            time TEXT NOT NULL,
            CONSTRAINT main_FK FOREIGN KEY (id) REFERENCES ip(id)
        );
        """,
        """
            CREATE TABLE "dhcp" (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            main_id INTEGER NOT NULL,
            time TEXT NOT NULL,
            mac TEXT,
            device TEXT,
            text TEXT NOT NULL,
            CONSTRAINT NewTable_FK FOREIGN KEY (id) REFERENCES main(id)
        );
        """,
        """
        CREATE TABLE dhcp2rad (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            main_id INTEGER NOT NULL,
            mac TEXT,
            time TEXT,
            text TEXT,
            CONSTRAINT dhcp2rad_FK FOREIGN KEY (id) REFERENCES main(id)
        );
        """
    ]
    #endregion
    
    def __init__(self, path=None):
        path = path or re.sub(r'.*?\/', "", BaseConfig.LOGS[0]) + ".db"
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self._drop_tables()
        self._create_tables()

    def _create_tables(self):
        for create in self.create_tables:
            self.execute(create)

    def _drop_tables(self):
        for drop in self.drop_tables:
            self.execute(drop)

    def execute(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def close(self):
        self.connection.close()

