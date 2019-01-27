#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, session, flash
import connexion
import model
import re
import dateutil.parser
import calendar


def get_ticker_price(ticker='aapl'):
    return model.apiget(ticker)

# app = connexion.App(__name__, specification_dir='./')

app = Flask(__name__)

# app.add_api('swagger.yml')

app.secret_key = 'the session needs this'

def date_format(datestring):
    date = dateutil.parser.parse(datestring)
    week_day_index = date.weekday()
    clock_time = date.strftime("%H:%M:%S")
    date_string = f"{calendar.day_abbr[week_day_index]} {date.day} {calendar.month_name[date.month]} "+ clock_time
    return date_string
    
# context_processor does not work with connexion
# @app.context_processor
# def context_processor():
#     return dict(date_format = date_format)



@app.route('/', methods=['GET'])
def send_to_login():
        return redirect('/login')

def set_user_object(username):
    user_object = model.Account(username)
    user_object = user_object.set_from_username()
    return user_object



@app.route('/login', methods=['GET', 'POST'])
def login():    
    if request.method == 'GET':
        print(session)
        if 'username' in session:
            return render_template('login_logged.html')
        return render_template('login.html')
    else:
        try:
            username = request.form['username']
            password = request.form['password']
            user_object = model.set_user_object(username)
        except:
            flash("Invalid Login")
            return redirect('/login')
        if user_object.check_password(user_object.pass_hash, password):
            session['username'] = username
            flash(f'User {username} successfully logged in!')
            return redirect('/login')
        else:
            flash("Invalid Login")
            return redirect('/login')

@app.route('/create_account', methods=['GET', 'POST'])
def create_new_account():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('create_account_logged.html')
        return render_template('create_account.html')
    else:
        username = request.form['username']
        password = request.form['password']
        model.Account(username)
        new_user = model.Account(username)
        print(new_user)
        if new_user.check_set_username():
            flash('User Already Exists')
            return redirect('/create_account')
        if len(password) < 8:
            flash('Please enter a password that is at least 8 characters')
            return redirect('/create_account')
        if re.search('[0-9]',password) is None:
            flash('Please enter a password that has at least one digit')
            return redirect('/create_account')
        if re.search('[A-Z]',password) is None:
            print('pass char')
            flash('Please enter a password that with at least one capital letter')
            return redirect('create_account')
        print('no issues')
        hashed_pw = new_user.calculatehash(password)
        print(hashed_pw)
        new_user.pass_hash = hashed_pw
        new_user.balance = 0
        new_user.type = "USER"
        new_user.save()
        flash('User Account Successfully Created')
        return redirect('/login')

@app.route('/homepage', methods=['GET'])
def show_homepage():
    return render_template('success.html', username=session['username'])

@app.route('/logout', methods=['GET'])
def log_out():
    session.clear()
    flash(f'User logged out')
    return redirect('/login')

@app.route('/check_stock_price', methods=['GET', 'POST'])
def check_stock_price():
    if request.method == 'GET':
        if 'username' in session:    
            return redirect('/check_stock_price_logged')
        else:
            return render_template('check_stock_price.html')
    else:
        ticker_symbol = request.form['ticker_symbol'].upper()
        price = model.apiget(ticker_symbol)
        flash(f'The Price of {ticker_symbol} is currently ${price}')
        return redirect('/check_stock_price')

@app.route('/check_stock_price_logged', methods=['GET', 'POST'])
def check_stock_price_logged():
    if request.method == 'GET':    
        if 'username' in session:    
            return render_template('check_stock_price_logged.html')
        else:
            return redirect('/check_stock_price')
    else:
        ticker_symbol = request.form['ticker_symbol']
        price = model.apiget(ticker_symbol).upper()
        flash(f'The Price of {ticker_symbol} is currently ${price}')
        return redirect('/check_stock_price_logged')
    
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('buy.html')
        else:
            flash('You will need to log in before you can make purchases')    
            return redirect('/login')
    else:
        try:
            ticker_symbol = request.form['ticker_symbol'].upper()
            number_of_shares = int(request.form['number_of_shares'])
            total_price = model.apiget(ticker_symbol)*number_of_shares
        except:
            flash('Invalid Entry! Try Again..') 
        flash(total_price)
        return redirect('/buy')

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('sell.html')
        else:
            flash('You will need to log in before you can sell your holdings')    
            return redirect('/login')
    else:
        #TODO: add sell logic
        ticker_symbol = request.form['ticker_symbol'].upper()
        price = model.apiget(ticker_symbol)
        flash(f'The Price of {ticker_symbol} is currently ${price}')
        return redirect('/check_stock_price')

@app.route('/portfolio', methods=['GET'])
def portfolio():
    if request.method == 'GET':
        if 'username' in session:
            user_object = model.set_user_object(session['username'])
            xs = user_object.getpositions_array()
            return render_template('portfolio.html', message = xs)
        else:
            flash('You will need to log in before you can sell your holdings')    
            return redirect('/login')


@app.route('/trade_history', methods=['GET'])
def trade_history():
    if request.method == 'GET':
        if 'username' in session:
            user_object = model.set_user_object(session['username'])
            xs = user_object.gettrades_array()
            return render_template('trade_history.html', message = xs)
        else:
            flash('You will need to log in before you can see your trade history')    
            return redirect('/login')
            
@app.route('/deposit_funds', methods=['GET'])
def deposit_funds():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('deposit_funds.html')
        else:
            flash('You will need to log in before you can deposit funds')    
            return redirect('/login')


@app.route('/news_scroll', methods=['GET'])
def news_scroll():
    content = model.return_top_headlines_content()
    content_len = len(content["articles"])
    return render_template('news_scroll.html', content = content, content_len = content_len)



if __name__=='__main__':
    app.debug = True
    app.run(port=8080)
    
