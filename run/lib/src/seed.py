import sqlite3
from time import time
import hashlib
import uuid


CON = None
CUR = None


def calculatehash(password):
    hashobject = hashlib.sha256()
    salt = "!$33gl3d33g"
    saltedstring = password.encode() + salt.encode()
    hashobject.update(saltedstring)
    return hashobject.hexdigest()


def setup(dbname="wtrader.db"):
    global CON
    global CUR
    CON = sqlite3.connect(dbname)
    CUR = CON.cursor()


def run():
    SQL = "DELETE FROM accounts;"
    CUR.execute(SQL)

    SQL = "DELETE FROM sqlite_sequence WHERE name = 'accounts';"
    CUR.execute(SQL)

    SQL = """INSERT INTO accounts(username, pass_hash, balance, type)
    VALUES(?, ?, ?, ?);"""
    pw_hash = calculatehash("password")
    CUR.execute(SQL, ("carter", pw_hash, 10000.0, 'USER'))
    CUR.execute(SQL, ("admin", pw_hash, 10000.0, 'ADMIN'))
   
    SQL = "DELETE FROM trades;"
    CUR.execute(SQL)

    SQL = "DELETE FROM sqlite_sequence WHERE name = 'trades';"
    CUR.execute(SQL)

    SQL = """INSERT INTO trades(account_pk, ticker, volume, price, time) 
    VALUES(?, ?, ?, ?, ?);"""
    CUR.execute(SQL, (1, "AAPL", 10, 100.0, int(time())))
    CUR.execute(SQL, (1, "TSLA", -1, 300.0, int(time())))

    SQL = "DELETE FROM sqlite_sequence WHERE name = 'positions';"
    CUR.execute(SQL)

    SQL = "DELETE FROM positions;"
    CUR.execute(SQL)

    SQL = """INSERT INTO positions(account_pk, ticker, amount) 
    VALUES(?, ?, ?);"""
    CUR.execute(SQL, (1, "AAPL", 10))
    CUR.execute(SQL, (1, "TSLA", 0))
    
    CON.commit()
    CUR.close()
    CON.close()


if __name__ == "__main__":
    setup()
    run()
