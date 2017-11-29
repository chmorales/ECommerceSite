from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for
import pymysql
from db_connector import get_connector
from functools import wraps


class Item:
    def __init__(self, item_id, name, description, price, seller, quantity,
                 category):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.price = price
        self.seller = seller
        self.quantity = quantity
        self.category = category
        self.total_price = None
        if self.price is not None and self.quantity is not None:
            self.total_price = self.price * self.quantity


class Review:
    def __init__(self, rating, description, first_name, last_name):
        self.rating = rating
        self.description = description
        self.first_name = first_name
        self.last_name = last_name


app = Flask(__name__)
app.secret_key = '$ombraM@inBTW'


def requires_log_in(func):
    """ Decorates a function, requiring that the user be logged in """
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return wrapped


@app.route("/", methods=['GET', 'POST'])
def index():
    error = None
    create_error = None
    if request.method == 'POST':
        if 'create_account' in request.form:
            cnx = get_connector()
            cursor = cnx.cursor()

            # We need the email address, password, firstname, and lastname.
            email_address = request.form['email']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']

            # Create a new cart just for our user. 
            query = 'INSERT INTO cart (price) VALUES (%f);' % (0.0)
            cursor.execute(query)

            # Commit the newly added cart to the database.
            cnx.commit()

            # The one we just added will be the last one, AKA the max.
            query = 'SELECT MAX(id) FROM cart;'
            cursor.execute(query)
            cart_id = int(cursor.fetchall()[0][0])

            try:
                # Insert the new user into the database.
                query = 'INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES (%s, %s, %s, %s, %s);'
                data = (first_name, last_name, password, email_address, cart_id)
                cursor.execute(query, data)

                # Save the userId into the session.
                query = 'SELECT MAX(id) FROM person;'
                cursor.execute(query)
                user_id = int(cursor.fetchall()[0][0])
                session['user_id'] = user_id

                # Commit, close, and redirect.
                cnx.commit()
                cnx.close()

                return redirect(url_for('hello'))

            except pymysql.err.IntegrityError:
                # Should only fire if the email address already exists in the database.
                create_error = 'That email is already taken. Please try a new email.'
                query = 'DELETE FROM cart WHERE id = %s;'
                data = (cart_id, )
                cursor.execute(query, data)

                cnx.commit()

        if 'log_in' in request.form:
            cnx = get_connector()
            cursor = cnx.cursor()
            email_address = request.form['email2']
            password = request.form['password2']

            # Doing it this way prevents an injection attack (allegedly).
            query = ("SELECT u.first_name, u.id FROM person u WHERE u.email_address = %s AND u.password = %s;")
            data = (email_address, password)
            cursor.execute(query, data)
            for (first_name, user_id) in cursor:
                session['user_id'] = user_id
                return redirect(url_for('hello'))
            error = 'Invalid email/password combination.'

        if 'search_input' in request.form:
            search_string = request.form['search_input']
            return redirect(url_for('search_results', string=search_string))

        cnx.close()
    return render_template('homepage.html', error=error, create_error=create_error)


@app.route("/cart", methods=['GET', 'POST'])
@requires_log_in
def shopping_cart():
    # Gets the user's id from the session.
    user_id = session['user_id']

    # Get the database connection and the cursor.
    cnx = get_connector()
    cursor = cnx.cursor()

    if request.method == 'POST':
        pass

    # Gets the current user's cartId.
    curr_cart_id = None
    query = 'SELECT p.cartId FROM person p WHERE p.id = %s;'
    data = (user_id, )
    cursor.execute(query, data)
    for (cart_id, ) in cursor:
        curr_cart_id = cart_id

    # Gets a list of item ids in the cart.
    item_ids = []
    quantities = {}
    query = 'SELECT i.itemId, i.quantity FROM takenItem i WHERE i.cartId = %s;'
    data = (curr_cart_id, )
    cursor.execute(query, data)
    for (item_id, quantity) in cursor:
        item_ids.append(item_id)
        quantities[item_id] = quantity

    # Get the relevant information from the item table.
    items = []
    for item_id in item_ids:
        query = 'SELECT i.name, i.description, i.price, i.seller_id FROM item i WHERE i.id = %s;'
        data = (item_id, )
        cursor.execute(query, data)
        for (name, description, price, seller_id) in cursor:
            # Get the email of the seller.
            cnx2 = get_connector()
            cursor2 = cnx2.cursor()
            query = 'SELECT p.email_address FROM person p WHERE p.id = %s;'
            data = (seller_id, )
            cursor2.execute(query, data)
            email_address = None
            for (email, ) in cursor2:
                email_address = email

            # Construct and append the object.
            items.append(Item(item_id, name, description, price, email_address, quantities[item_id], None))

    return render_template('cart.html', items=items)


@app.route("/cart/remove/<int:item_id>", methods=['POST'])
@requires_log_in
def remove_from_cart(item_id):
    user_id = session['user_id']
    cnx = get_connector()
    cursor = cnx.cursor()

    # Getting the users cart id
    query = "SELECT p.cartId FROM person p WHERE p.id = %s;"
    data = (user_id, )
    cursor.execute(query, data)
    cart_id = None
    for (cart, ) in cursor:
        cart_id = cart

    # Update the item listing to have one more
    query = "UPDATE item SET quantity = quantity + 1 WHERE id = %s;"
    data = (item_id, )
    cursor.execute(query, data)

    # Get the quantity of the item that's in the cart
    query = "SELECT t.quantity FROM takenItem t WHERE t.itemId = %s AND t.cartId = %s;"
    data = (item_id, cart_id)
    cursor.execute(query, data)
    quantity = None
    for (quant, ) in cursor:
        quantity = quant

    # Sets the data for the last query
    data = (item_id, cart_id)

    if quantity == 1:
        # If there was only one item left, remove it from the table
        query = "DELETE FROM takenItem WHERE itemId = %s AND cartId = %s;"
        cursor.execute(query, data)
    else:
        # Otherwise remove one of the item from the cart
        query = "UPDATE takenItem SET quantity = quantity - 1 WHERE itemId = %s AND cartId = %s;"
        cursor.execute(query, data)

    cnx.commit()
    cnx.close()

    return redirect(url_for('shopping_cart'))


@app.route("/hello")
def hello():
    print(session['user_id'])
    return render_template('test.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_string = request.form['search_string']
        return redirect(url_for('search_results', string=search_string))
    return render_template('search.html')


@app.route('/search/<string:string>', methods=['GET', 'POST'])
def search_results(string):
    if request.method == 'POST':
        search_string = request.form['search_input']
        return redirect(url_for('search_results', string=search_string))

    # Get the database connection.
    cnx = get_connector()
    cursor = cnx.cursor()

    # Search for any items with a name containing the search string.
    query = 'SELECT i.id, i.name, i.description, i.price, i.quantity FROM item i WHERE i.name LIKE %s;'
    data = ('%' + string + '%', )
    cursor.execute(query, data)

    # Save the results into a list of items.
    items = []
    for (item_id, name, description, price, quantity) in cursor:
        items.append(Item(item_id, name, description, price, None, quantity, None))

    cnx.close()
    return render_template('search_results.html', items=items, search_string=string)


@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item_page(item_id):
    # Gets database connection.
    cnx = get_connector()
    cursor = cnx.cursor()

    if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))
        user_id = session['user_id']

        query = 'SELECT i.quantity FROM item i WHERE i.id = %s;'
        data = (item_id, )
        cursor.execute(query, data)
        num = None
        for (result, ) in cursor:
            num = result

        if num > 0:
            # Decrease the number of availible items by 1.
            query = 'UPDATE item SET quantity = quantity - 1 WHERE id = %s;'
            data = (item_id, )
            cursor.execute(query, data)

            # Gets the current user's cart id.
            query = 'SELECT p.cartId FROM person p WHERE p.id = %s;'
            data = (user_id, )
            cursor.execute(query, data)
            cart_id = None
            for (cart, ) in cursor:
                cart_id = cart

            exists = False
            query = 'SELECT i.itemId FROM takenItem i WHERE i.itemId = %s;'
            data = (item_id, )
            cursor.execute(query, data)
            for item in cursor:
                exists = True

            if exists:
                query = 'UPDATE takenItem SET quantity = quantity + 1 WHERE itemId = %s;'
                data = (item_id, )
                cursor.execute(query, data)

            if not exists:
                query = 'INSERT INTO takenItem (itemId, cartId, quantity) VALUES (%s, %s, %s);'
                data = (item_id, cart_id, 1)
                cursor.execute(query, data)

        cnx.commit()

    # Gets relevant information from item table.
    query = 'SELECT i.name, i.description, i.price, i.seller_id, i.quantity, i.category_id FROM item i WHERE i.id = %s;'
    data = (item_id, )
    cursor.execute(query, data)

    # Walks through result, setting up object.
    item = None
    for (name, description, price, seller_id, quantity, category_id) in cursor:
        # Gets another database connection.
        cnx2 = get_connector()
        cursor2 = cnx2.cursor()

        # Gets the seller's email address.
        query = 'SELECT s.email_address FROM person s WHERE s.id = %s;'
        data = (seller_id, )
        cursor2.execute(query, data)
        email = None
        for (user, ) in cursor2:
            email = user

        # Gets the actual name of the category.
        query = 'SELECT c.name FROM category c WHERE c.id = %s;'
        data = (category_id, )
        cursor2.execute(query, data)
        category = None
        for (category_name, ) in cursor2:
            category = category_name

        # Creates the full Item object.
        item = Item(item_id, name, description, price, email, quantity, category)
        cnx2.close()

    # Gets the relevant review information.
    query = ('SELECT r.rating, r.description, r.userId FROM review r WHERE r.itemId = %s;')
    data = (item_id, )
    cursor.execute(query, data)

    # Iterates through the cursor information to construct the Review object.
    reviews = []
    for (rating, description, user_id) in cursor:
        cnx2 = get_connector()
        cursor2 = cnx2.cursor()
        # Gets the first and last name of the person who wrote the review.
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

    return render_template('item.html', item=item, ratings=reviews)


@app.route('/sell_item', methods=['GET', 'POST'])
@requires_log_in
def sell_item():
    error = None

    cnx = get_connector()
    cursor = cnx.cursor()

    if request.method == 'POST':

        try:
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            quantity = int(request.form['quantity'])
            category_name = request.form['category']

            query = 'SELECT c.id FROM category c WHERE c.name = %s'
            data = (category_name, )
            cursor.execute(query, data)
            category_id = None
            for (category_id_result, ) in cursor:
                category_id = category_id_result

            query = "INSERT INTO item (name, description, price, seller_id, quantity, category_id) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (name, description, price, session['user_id'], quantity, category_id)
            cursor.execute(query, data)

            cnx.commit()

        except ValueError:
            error = 'Please enter valid numbers for the quantity and price.'

    query = 'SELECT c.name FROM category c;'
    cursor.execute(query)

    categories = []
    for (category, ) in cursor:
        categories.append(category)

    cnx.close()

    return render_template('sell_item.html', error=error, categories=categories)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
