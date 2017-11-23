from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for
import mysql.connector

app = Flask(__name__)
  
@app.route("/")
def index():
    return "Flask App!"
       
@app.route("/hello/<string:name>/")
def hello(name):
    return render_template('test.html',name=name)
               
# Account creation page.
@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Going to have to figure something out about this. Everyone's database will have a different root password. 
        cnx = mysql.connector.connect(user='root', password='$ombraM@inBTW', host='104.196.6.60', database='CSE305')
        cursor = cnx.cursor()

        # We need the email address, the password, the firstname, and the lastname. 
        email_address = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # TODO: Add checks for validity.

        # Create a new cart just for our user. 
        query = 'INSERT INTO cart (price) VALUES (%f);' % (0.0)
        cursor.execute(query)

        # Commit the newly added cart to the database.
        cnx.commit()

        # The one we just added will be the last one, AKA the max.
        query = 'SELECT MAX(id) FROM cart'
        cursor.execute(query)
        cart_id = int(cursor.fetchall()[0][0])

        # Insert the new user into the database.
        query = "INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES (%s, %s, %s, %s, %s)"
        values = (first_name, last_name, password, email_address, cart_id)
        cursor.execute(query, values)

        # Commit and close.
        cnx.commit()
        cnx.close()

    return render_template('create_account2.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cnx = mysql.connector.connect(user='root', password='$ombraM@inBTW', host='104.196.6.60', database='CSE305')
        cursor = cnx.cursor(buffered=True)
        email_address = request.form['email']
        password = request.form['password']

        # Doing it this way prevents an injection attack (allegedly).
        query = ("SELECT u.first_name FROM person u WHERE u.email_address = %s AND u.password = %s;")
        data = (email_address, password)
        cursor.execute(query, data)
        if cursor.rowcount != 0:
            name = cursor.fetchall()[0][0]
            return redirect(url_for('hello', name=name))
        else:
            print('wrong')
        cursor.close()
        cnx.close()
    return render_template('log_in.html', error=error)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)



