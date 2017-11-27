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

class Review:
    def __init__(self, rating, description, first_name, last_name):
        self.rating = rating
        self.description = description
        self.first_name = first_name
        self.last_name = last_name

@app.route('/reviews/<int:item_id>', methods=['GET', 'POST'])
def reviews(item_id):
    # Gets the database connector and the cursor.
    cnx = get_connector()
    cursor = cnx.cursor()
    
    # Gets the name of the item being reviewed.
    query = ('SELECT i.name FROM item i WHERE i.id = %s;')
    data = (item_id, )
    cursor.execute(query, data)
    for (item_name, ) in cursor:
        item = item_name

    # Gets the relevant review information.
    query = ('SELECT r.rating, r.description, r.userId FROM review r WHERE r.itemId = %s;')
    data = (item_id, )
    cursor.execute(query, data)

    # Iterates through the cursor information to construct the Review object.
    reviews = []
    for (rating, description, user_id) in cursor:
        # Gets the first and last name of the person who wrote the review.
        cnx2 = get_connector()
        cursor2 = cnx2.cursor()
        query = ('SELECT p.first_name, p.last_name FROM person p WHERE p.id = %s')
        data = (user_id, )
        cursor2.execute(query, data)
        for (first_name, last_name) in cursor2:
            fn = first_name
            ln = last_name

        # Appends the Review item to the list of reviews.
        reviews.append(Review(rating, description, fn, ln))
        cnx2.close()
    cnx.close()

    return render_template('reviews.html', ratings=reviews, item_name=item)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)



