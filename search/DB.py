from .Config import BaseConfig, logger
import sqlite3
import re


class DB:
    # region create tables sql lines
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
            error TEXT,
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
        """,
    ]
    # endregion

    def __init__(self, path=None, *args, **kwargs):
        path = path or BaseConfig.LOGS
        dbname = re.sub(r".*?\/|\..*", "", path)
        self.path = "databases/{}.db".format(dbname)
        try:
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
            self._drop_tables()
            self._create_tables()
            logger.info("Database opened.")
        except:
            logger.error("Failed to open database. Path: {}".format(self.path))

    def _create_tables(self, *args, **kwargs):
        for create in self.create_tables:
            self.execute(create)

    def _drop_tables(self, *args, **kwargs):
        for drop in self.drop_tables:
            self.execute(drop)

    def execute(self, query, *args, **kwargs):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            logger.error("Failed to execute sql query. Query: {}".format(query))

    def close(self, *args, **kwargs):
        self.connection.close()
        logger.info("Data saved to file: {}".format(self.path))
