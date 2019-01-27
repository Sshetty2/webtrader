from random import randint
import sqlite3
import requests
import hashlib
import uuid
import time
from newsapi import NewsApiClient
import os.path


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "wtrader.db")

api = NewsApiClient(api_key='63ff7711014f4180801278336d4873f9')

CONFIG = {
    'SALT': "!$33gl3d33g",
    'DBNAME': db_path,
    "APIURL": "https://api.iextrading.com/1.0/stock/{}/quote",
    'FAKEPRICE': {
        'stck': 50.25
    }
}

def create_new_user(userid, password, user_type):
    try:
        user_object = Account(userid)
    except:
        return "username error"
    if user_object.check_set_username():
        return "userid already exists"
    hashed_pw = user_object.calculatehash(password)
    user_object.pass_hash = hashed_pw
    user_object.type = user_type
    user_object.save()

def create_new_user_query(userid, password, user_type):
    try:
        user_object = set_user_object(userid)
    except:
        return "username error"
    hashed_pw = user_object.calculatehash(password)
    user_object.pass_hash = hashed_pw
    user_object.type = user_type
    user_object.save()



def return_pass_hash(username):
    new_account_obj = Account(username=username)
    account_obj = new_account_obj.set_from_username()
    return account_obj.pass_hash

def validate_pw(userid, password):
    user_object = set_user_object(userid)
    if user_object.check_password(user_object.pass_hash, password):
        return True
    return False


def return_pass_hash(username):
    new_account_obj = Account(username=username)
    account_obj = new_account_obj.set_from_username()
    return account_obj.pass_hash

def validate_pw(userid, password):
    user_object = set_user_object(userid)
    if user_object.check_password(user_object.pass_hash, password):
        return True
    return False


DBNAME = "wtrader.db"


def return_top_headlines_content():
    content = api.get_top_headlines(sources='the-wall-street-journal')
    return content


def apiget(tick, url= "https://api.iextrading.com/1.0/stock/{}/quote"):
    URL = url.format(tick)
    try:
        data = requests.get(URL).json()
        price = data.get("latestPrice")
    except:
        price = None
    return price

def apiget_companyName(tick, url= "https://api.iextrading.com/1.0/stock/{}/company"):
    URL = url.format(tick)
    try:
        data = requests.get(URL).json()
        companyName = data.get("companyName")
    except:
        companyName = None
    return companyName
    
def apiget_companySector(tick, url= "https://api.iextrading.com/1.0/stock/{}/company"):
    URL = url.format(tick)
    try:
        data = requests.get(URL).json()
        companySector = data.get("sector")
    except:
        companySector = None
    return companySector



def getprice(symbol):
    return randint(5000, 20000) / 100

def print_gettrades(results_from_gettrades):
    for i in results_from_gettrades:
        print(i)

def print_all_accounts(all_accounts):
    for i in all_accounts:
        print(i)

def set_user_object(username):
    user_object = Account(username)
    user_object = user_object.set_from_username()
    return user_object


class OpenCursor:
    def __init__(self, *args, **kwargs):
        # update:
        if 'dbname' in kwargs:
            self.dbname = kwargs['dbname']
            del(kwargs['dbname'])
        else:
            self.dbname = CONFIG['DBNAME']

        self.conn = sqlite3.connect(self.dbname, *args, **kwargs)
        self.conn.row_factory = sqlite3.Row  # access fetch results by col name
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, extype, exvalue, extraceback):
        if not extype:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()


class Position:
    def __init__(self, account_pk=None, ticker=None, amount=None, pk=None):
        self.account_pk = account_pk
        self.ticker = ticker
        self.amount = amount
        self.pk = pk

    def save(self):
        with OpenCursor() as cur:
            if not self.pk:
                SQL = """
                INSERT INTO positions(account_pk, ticker, amount)
                VALUES(?, ?, ?);
                """
                cur.execute(SQL, (self.account_pk, self.ticker, self.amount))
                self.pk = cur.lastrowid

            else:
                SQL = """
                UPDATE positions SET account_pk=?, ticker=?, amount=? WHERE
                pk=?;
                """
                cur.execute(SQL, (self.account_pk, self.ticker, self.amount,
                                  self.pk))

    def set_from_row(self, row):
        self.pk = row["pk"]
        self.account_pk = row["account_pk"]
        self.ticker = row["ticker"]
        self.amount = row["amount"]
        return self

    def getvalue(self):
        return self.amount * apiget(self.ticker)

    def __repr__(self):
        display ="Position PK = {}: Stock = {}, amount = {}, Account PK = {} ".format(self.pk, self.ticker, self.amount, self.account_pk)
        return display

    def __str__(self):
        display ="Stock = {}, Number of Shares = {}, Position Value = {}".format(self.ticker, self.amount, round(self.getvalue(),2))
        return display
    #def getposition(self, pk):


class Trade:
    def __init__(self, pk = None, account_pk=None, ticker=None,
                 volume=None, price=None, time=None):
        self.pk = pk
        self.account_pk = account_pk
        self.ticker = ticker
        self.volume = volume
        self.price = price
        self.time = time

    def save(self):
        if self.time is None:
            self.time = time.asctime(time.localtime(time.time()))
        with OpenCursor() as cur:
            if not self.pk:
                SQL = """
                INSERT INTO trades(account_pk, ticker, volume, price, time)
                VALUES(?, ?, ?, ?, ?);
                """
                cur.execute(SQL, (self.account_pk, self.ticker, self.volume, self.price, self.time))
                self.pk = cur.lastrowid

            else:
                SQL = """
                UPDATE trades SET account_pk=?, ticker=?, price=?, time=? WHERE
                pk=?;
                """
                cur.execute(SQL, (self.account_pk, self.ticker, self.price, self.time,
                                    self.pk))

    def set_from_row(self, row):
        self.pk = row["pk"]
        self.account_pk = row["account_pk"]
        self.ticker = row["ticker"]
        self.volume = row["volume"]
        self.price = row["price"]
        self.time = row["time"]
        return self
    
    def __repr__(self):
        display ="Trade: pk = {}, Account pk = {}, Stock = {}, Volume = {}, Price = {}, Time = {}".format(self.pk, self.account_pk, self.ticker, self.volume, self.price, self.time)
        return display
    
    def __str__(self):
        display ="Stock = {}, Volume = {}, Price = {}, Time = {}".format(self.ticker, self.volume, round(self.price, 2), self.time)
        return display


class Account:
    def __init__(self, username=None, pass_hash=None, balance=None, user_type= None, pk=None):
        self.pk = pk
        self.username = username
        self.pass_hash = pass_hash
        self.balance = balance
        self.type = user_type


    def calculatehash(self, password):
        hashobject = hashlib.sha256()
        salt = CONFIG['SALT']
        saltedstring = password.encode() + salt.encode()
        hashobject.update(saltedstring)
        return hashobject.hexdigest()

    def check_password(self, hashed_password, user_password):
        hashobject = hashlib.sha256()
        salt = CONFIG['SALT']
        new_salted_string = user_password.encode() + salt.encode()
        hashobject.update(new_salted_string)
        new_hashed_pw = hashobject.hexdigest()
        if hashed_password == new_hashed_pw:
            return True
        return False

    def check_set_username(self):
        with OpenCursor() as cur: 
            SQL = """
            SELECT * FROM accounts WHERE username = ?;
            """
            cur.execute(SQL, (self.username, ))
            row=cur.fetchone()   
        if not row:
            return False
        self.set_from_row(row)
        # if the username is found, the attributes are set 
        return True

    def set_from_username(self):
        with OpenCursor() as cur: 
            SQL = """
            SELECT * FROM accounts WHERE username = ?;
            """
            cur.execute(SQL, (self.username, ))
            row=cur.fetchone()  
        self.set_from_row(row)
        return self
        


    # def set_from_credentials(self, username, password):
    #     with OpenCursor() as cur: 
    #         SQL = """
    #         SELECT * FROM accounts WHERE username = ?;
    #         """

    #         #self.set from row 

        # if not row:
        #     return False



    def __bool__(self):
        return bool(self.pk)
    

    def save(self):
        with OpenCursor() as cur:
            if not self.pk:
                SQL = """
                INSERT INTO accounts(username, pass_hash, balance, type)
                VALUES(?, ?, ?, ?);
                """
                cur.execute(SQL, (self.username, self.pass_hash, self.balance, self.type))
                self.pk = cur.lastrowid

            else:
                SQL = """
                UPDATE accounts SET username=?, pass_hash=?, balance=? WHERE
                pk=?;
                """
                cur.execute(SQL, (self.username, self.pass_hash, self.balance,
                                  self.pk))
    def __repr__(self):
        display ="Account PK = {}, Username = {}, PW Hash = {}, Balance = {}".format(self.pk, self.username, self.pass_hash, self.balance)
        return display

    def set_from_row(self, row):
        self.pk = row["pk"]
        self.username = row["username"]
        self.pass_hash = row["pass_hash"]
        self.balance = row["balance"]
        self.type = row["type"]
        return self

    def set_from_pk(self, pk):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM accounts WHERE pk = ?;
            """
            cur.execute(SQL, (pk,))
            row = cur.fetchone()
            if not row:
                raise KeyError("Account with pk does not exist")
            self.set_from_row(row)

            """ given a pk, get the row of that user from the database and pass it
            to set_from_row"""
        return self
    
    def getpositions(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM positions WHERE account_pk = ?;
            """
            cur.execute(SQL, (self.pk,))
            rows = cur.fetchall()
            results = []
            for row in rows: 
                pos = Position()
                pos.set_from_row(row)
                results.append(pos)
            return results


    def getpositions_array(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM positions WHERE account_pk = ?;
            """
            cur.execute(SQL, (self.pk,))
            rows = cur.fetchall()
            results = []
            for row in rows:
                row_place = []
                row_place.append(apiget_companyName((row["ticker"]))) 
                row_place.append(row["ticker"]) 
                row_place.append(row["amount"]) 
                row_place.append(round(apiget(row["ticker"]),2)) 
                row_place.append(round(apiget(row["ticker"]),2)*row["amount"]) 
                results.append(row_place)
            return results

    def get_all_accounts(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM accounts;
            """
            cur.execute(SQL)
            rows = cur.fetchall()
            results = []
            for row in rows: 
                acc = Account()
                acc.set_from_row(row)
                results.append(acc)
            return results

    def getposition(self, ticker):
        with OpenCursor() as cur: 
            SQL = """
            SELECT * FROM positions WHERE account_pk = ? AND ticker=?;
            """
            cur.execute(SQL, (self.pk, ticker))
            row = cur.fetchone()
            if not row:
                return None
            pos = Position()
        return pos.set_from_row(row)
    
    
    def increase_position(self, ticker, amount):
        pos = self.getposition(str(ticker))
        if (apiget(ticker) * int(amount)) > self.balance:
            raise ValueError("insufficient funds")
        elif not pos:
            pos = Position(account_pk = self.pk, ticker = ticker, amount = 0)
        pos.amount += amount
        pos.save()
    
    def decrease_position(self, ticker, amount):
        pos = self.getposition(ticker)
        if not pos:
            raise ValueError("Position doesn't exist")
        elif pos.amount < amount:
            raise ValueError("You do not own enough shares")
        if pos.amount == amount:
            with OpenCursor() as cur: 
                SQL = """
                DELETE FROM positions WHERE ticker = ? AND account_pk = ?;
                """
                cur.execute(SQL, (ticker, self.pk))
        else: 
            pos.amount -= amount
            pos.save()

    def gettrades(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM trades WHERE account_pk = ?;
            """
            cur.execute(SQL, (self.pk,))
            rows = cur.fetchall()
            results = []
            for row in rows: 
                trade = Trade()
                trade.set_from_row(row)
                results.append(trade)
            return results
        
    def gettrades_array(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM trades WHERE account_pk = ?;
            """
            cur.execute(SQL, (self.pk,))
            rows = cur.fetchall()
            results = []
            for row in rows:
                row_place = []
                row_place.append(row["time"]) 
                row_place.append(row["ticker"])
                row_place.append(apiget_companyName((row["ticker"])))  
                row_place.append(row["price"]) 
                row_place.append(row["volume"]) 
                row_place.append(row["price"]*row["volume"]) 
                results.append(row_place)
            return results


    def gettradesfor(self, ticker):
        with OpenCursor() as cur: 
            SQL = """
            SELECT * FROM trades WHERE account_pk = ? AND ticker=? 
            """
            cur.execute(SQL, (self.pk, ticker))
            rows = cur.fetchall()
            results = []
            for row in rows: 
                trade = Trade()
                trade.set_from_row(row)
                results.append(trade)
        return results
    
    def sell(self, ticker, volume, price=None):
        if price is None:
            price = apiget(ticker)
        try:
            self.decrease_position(ticker, amount = volume)
        except ValueError:
            raise ValueError("insufficient funds")
        trade = Trade(pk = None, account_pk = self.pk, ticker= ticker, volume=volume*-1, price=price, time=None)
        self.balance += volume * price
        trade.save()
        self.save()

    def buy(self, ticker, volume, price=None):
        if price is None:
            price = apiget(ticker)
        try:
            self.increase_position(ticker, volume)
        except ValueError: 
            raise ValueError("insufficient funds")
        trade = Trade(pk = None, account_pk = self.pk, ticker = ticker, volume=volume, price=price, time=None)
        self.balance -= volume * price
        trade.save()
        self.save()
        return True
        
    def set_balance(self, amt_of_funds):
        try:
            with OpenCursor() as cur:
                SQL = """
                UPDATE accounts SET balance = ? WHERE pk = ?;
                """
                cur.execute(SQL, (amt_of_funds, self.pk))
            self.balance = amt_of_funds
        except:
            print('could not update balance')
        self.save()
        return self
    
    def deposit_funds(self, amt_of_funds):
        try:
            with OpenCursor() as cur:
                SQL = """
                UPDATE accounts SET balance = ? WHERE pk = ?;
                """
                cur.execute(SQL, (amt_of_funds, self.pk))
            self.balance = amt_of_funds + self.balance
        except:
            print('could not update balance')
        self.save()
        return self

