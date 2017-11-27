from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for
import mysql.connector
from db_connector import get_connector

app = Flask(__name__)
app.secret_key = '$ombraM@inBTW'
  
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'create_account' in request.form:
            # Going to have to figure something out about this. Everyone's database will have a different root password. 
            cnx = get_connector()
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
            query = 'SELECT MAX(id) FROM cart;'
            cursor.execute(query)
            cart_id = int(cursor.fetchall()[0][0])

            # Insert the new user into the database.
            query = 'INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES (%s, %s, %s, %s, %s);'
            values = (first_name, last_name, password, email_address, cart_id)
            cursor.execute(query, values)

            query = 'SELECT MAX(id) FROM person;'
            cursor.execute(query)
            user_id = int(cursor.fetchall()[0][0])
            session['user_id'] = user_id

            # Commit and close.
            cnx.commit()
            cnx.close()

            return redirect(url_for('hello'))

        if 'log_in' in request.form:
            cnx = get_connector()
            cursor = cnx.cursor(buffered=True)
            email_address = request.form['email']
            password = request.form['password']

            # Doing it this way prevents an injection attack (allegedly).
            query = ("SELECT u.first_name, u.id FROM person u WHERE u.email_address = %s AND u.password = %s;")
            data = (email_address, password)
            cursor.execute(query, data)
            for (first_name, user_id) in cursor:
                session['user_id'] = user_id
                return redirect(url_for('hello'))
        cnx.close()
    return render_template('homepage.html')
       
@app.route("/hello")
def hello():
    return render_template('test.html')

@app.route('/sell_item', methods=['GET', 'POST'])
def sell_item():
    if request.method == 'POST':
        cnx = get_connector()
        cursor = cnx.cursor()

        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        category_id = 1
        # category_name = request.form['category']

        # query = 'SELECT c.id FROM category c WHERE c.name = %s'
        # data = (category_name)
        # cursor.execute(query, data)
        # category_id = int(cursor.fetchall()[0][0])

        query = "INSERT INTO item (name, description, price, seller_id, quantity, category_id) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (name, description, price, session['user_id'], quantity, category_id)
        cursor.execute(query, data)

        cnx.commit()

        cnx.close()
    return render_template('sell_item.html')

@app.route('/reviews/<int:item_id>', methods=['GET', 'POST'])
def reviews(item_id):
    cnx = get_connector()
    cursor = cnx.cursor()

    query = ('SELECT r.rating, r.description FROM review r WHERE r.itemId = %s;')
    data = (item_id, )
    cursor.execute(query, data)

    ratings = []
    descriptions = []
    for (rating, description) in cursor:
        ratings.append(rating)
        descriptions.append(description)

    cnx.close()

    return render_template('reviews.html', ratings=ratings, descriptions=descriptions)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)



