from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for
import mysql.connector

app = Flask(__name__)
  
@app.route("/")
def index():
    return "Flask App!"
       
@app.route("/hello/<string:name>/")
def hello(name):
    return render_template('test.html',name=name)
               
@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
    	cnx = mysql.connector.connect(user='root', password='noobama12', host='127.0.0.1', database='users')
    	cursor = cnx.cursor()
    	user = request.form['username']
    	passw = request.form['password']
    	query = 'INSERT INTO user (username, password) VALUES (\'%s\', \'%s\');' % (user, passw)
    	print(query)
    	cursor.execute(query)
    	print(cursor.lastrowid)
    	cursor.close()
    	cnx.commit()
    	cnx.close()
    return render_template('create_account2.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
    	cnx = mysql.connector.connect(user='root', password='noobama12', host='127.0.0.1', database='users')
    	cursor = cnx.cursor(buffered=True)
    	user = request.form['username']
    	passw = request.form['password']
    	query = 'SELECT u.password FROM user u WHERE u.username = \'%s\' AND u.password = \'%s\';' % (user, passw)
    	print(query)
    	cursor.execute(query)
    	if cursor.rowcount != 0:
    			return redirect(url_for('hello', name=user))
    	else:
    		print('wrong:wq')
    	cursor.close()
    	cnx.close()
    return render_template('create_account2.html', error=error)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
