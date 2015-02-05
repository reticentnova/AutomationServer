import sqlite3

class DatabaseManager(object):
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()

    def query(self, arg):
        self.cur.execute(arg)
        self.conn.commit()
        return self.cur

    def updateInfo(self,command, key, expires):             
        self.cur.execute(command, (key,expires))
        self.conn.commit()
        return self.cur

    def __del__(self):
        self.conn.close()
