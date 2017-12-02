from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for
import pymysql
from db_connector import get_connector
from functools import wraps
import os

UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def requires_log_in(func):
    """ Decorates a function, requiring that the user be logged in """
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapped


def user_id_decorator(func):
    """ Wraps a function to add the user id to it's kwargs """
    @wraps(func)
    def temp_with_user_id(*args, **kwargs):
        user_id = None
        logged_in = False
        first_name = None
        if 'user_id' in session:
            user_id = session['user_id']
            first_name = session['first_name']
            logged_in = True

        kwargs['user_id'] = user_id
        kwargs['logged_in'] = logged_in
        kwargs['first_name'] = first_name
        return func(*args, **kwargs)
    return temp_with_user_id


# Redefines render_template to inlude user_id and logged_in variables
render_template = user_id_decorator(render_template)


def get_item(item_id):
    cnx = get_connector()
    cursor = cnx.cursor()
    query = 'SELECT i.name, i.description, i.price, i.quantity, s.email_address, c.name FROM item i, person s, category c WHERE i.id = %s AND i.category_id = c.id AND i.seller_id = s.id;'
    data = (item_id, )
    cursor.execute(query, data)
    item = None
    for (name, description, price, quantity, email_address, category_name) in cursor:
        item = Item(item_id, name, description, price, email_address, quantity, category_name)
    cnx.close()
    return item


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def index():
    cnx = get_connector()
    cursor = cnx.cursor()
    query = ("SELECT itemId FROM featuredItem;")
    cursor.execute(query)

    items = []
    for (item_id, ) in cursor:
        items.append(get_item(item_id))
    return render_template('homepage.html', items=items)


@app.route("/login", methods=['GET', 'POST'])
def login():
    error=None
    create_error=None

    if request.method == 'POST':
        if 'login' in request.form:
            cnx = get_connector()
            cursor = cnx.cursor()
            email = request.form['login_email']
            password = request.form['login_password']

            # Using prepared statements to prevent SQL injection
            query = ("SELECT u.first_name, u.id FROM person u WHERE u.email_address = %s AND u.password = %s;")
            data = (email, password)
            cursor.execute(query, data)

            for (first_name, user_id) in cursor:
                session['user_id'] = user_id
                session['first_name'] = first_name
                return redirect(url_for('index'))
            error = 'Invalid email and password combonation.'
            return render_template('login.html', error=error, create_error=create_error)

        elif 'create_account' in request.form:
            cnx = get_connector()
            cursor = cnx.cursor()

            # We need the email address, password, firstname, and lastname.
            email_address = request.form['create_email']
            password = request.form['create_password']
            first_name = request.form['create_first_name']
            last_name = request.form['create_last_name']

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
                session['first_name'] = first_name

                query = 'UPDATE cart SET userId = %s WHERE id = %s;'
                data = (user_id, cart_id)
                cursor.execute(query, data)

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
                return render_template('login.html', error=error, create_error=create_error)

        elif 'search_input' in request.form:
            search_string = request.form['search_input']
            return redirect(url_for('search_results', string=search_string))

        cnx.close()
    return render_template('login.html', error=error, create_error=create_error)


@app.route('/logout')
@requires_log_in
def logout():
    session.pop('user_id', None)
    session.pop('first_name', None)
    return redirect(url_for('index'))


@app.route("/cart", methods=['POST', 'GET'])
@requires_log_in
def shopping_cart():
    # Gets the user's id from the session.
    user_id = session['user_id']

    # Get the database connection and the cursor.
    cnx = get_connector()
    cursor = cnx.cursor()

    # User is trying to buy the cart.
    if request.method == 'POST':

        # Get the current user's cartId.
        query = 'SELECT p.cartId FROM person p WHERE p.id = %s;'
        data = (user_id, )
        cursor.execute(query, data)
        cart_id = None
        for (result, ) in cursor:
            cart_id = result

        # Insert a new cart into the system.
        query = 'INSERT INTO cart (price, userId) VALUES (%s, %s);'
        data = (0.0, user_id)
        cursor.execute(query, data)

        # Get the newest added cart for the current user.
        query = 'SELECT MAX(c.id) FROM cart c WHERE c.userId = %s;'
        data = (user_id, )
        cursor.execute(query, data)
        cart_num = None
        for (result, ) in cursor:
            cart_num = result

        # Update the user's cart to that one.
        query = 'UPDATE person SET cartId = %s WHERE id = %s;'
        data = (cart_num, user_id)
        cursor.execute(query, data)

        # Put the old cart into a saved purchase slot.
        query = 'INSERT INTO purchase (buyerId, cartId, purchaseDate) VALUES (%s, %s, NOW());'
        data = (user_id, cart_id)
        cursor.execute(query, data)

        cnx.commit()

    # Gets the current user's cartId.
    curr_cart_id = None
    query = 'SELECT p.cartId FROM person p WHERE p.id = %s;'
    data = (user_id, )
    cursor.execute(query, data)
    for (cart_id, ) in cursor:
        curr_cart_id = cart_id

    query = 'SELECT c.price FROM cart c WHERE c.id = %s;'
    data = (cart_id, )
    cursor.execute(query, data)
    cart_price = None
    for (result, ) in cursor:
        cart_price = result

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
        query = 'SELECT i.name, i.description, i.price, p.email_address FROM item i, person p WHERE i.seller_id = p.id AND i.id = %s;'
        data = (item_id, )
        cursor.execute(query, data)
        for (name, description, price, email_address) in cursor:
            # Construct and append the object.
            items.append(Item(item_id, name, description, price, email_address, quantities[item_id], None))

    return render_template('cart.html', items=items, cart_price=cart_price)


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

    query = 'SELECT i.price FROM item i WHERE i.id = %s;'
    data = (item_id, )
    cursor.execute(query, data)
    item_price = None
    for(result, ) in cursor:
        item_price = result

    query = 'UPDATE cart SET price = price - %s WHERE id = %s;'
    data = (item_price, cart_id)
    cursor.execute(query, data)

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


@app.route('/sale_history', methods=['GET', 'POST'])
@requires_log_in
def sales():
    error = None
    user_id = session['user_id']
    cnx = get_connector()
    cursor = cnx.cursor()

    # Get the items that have been sold by the current user, and their
    query = ("SELECT i.id, i.name, i.price, t.quantity, p.purchaseDate "
             "FROM item i, takenItem t, cart c, purchase p "
             "WHERE i.id = t.itemId AND i.seller_id = %s AND c.id = p.cartId;")
    data = (user_id, )
    cursor.execute(query, data)

    purchases = []

    # Make a list of all the purchases we will be displaying.
    for (item_id, item_name, price, quantity, purchase_date) in cursor:
        purchases.append(Purchase(item_id=item_id, item=item_name,
                                  date=purchase_date, price=price,
                                  seller=None, quantity=quantity))

    cnx.close()

    return render_template('sale_history.html', error=error, purchases=purchases)


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        search_string = request.form['search_input']
        return redirect(url_for('search_results', string=search_string))


@app.route('/search/<string:string>', methods=['GET', 'POST'])
def search_results(string):
    if request.method == 'POST':
        search_string = request.form['search_input']
        return redirect(url_for('search_results.html', string=search_string))

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

        query = 'SELECT i.quantity, i.price FROM item i WHERE i.id = %s;'
        data = (item_id, )
        cursor.execute(query, data)
        num = None
        price = None
        for (result, result2 ) in cursor:
            num = result
            price = result2

        print(price)

        query = 'UPDATE cart SET price = price + %s WHERE userId = %s;'
        data = (price, user_id)
        cursor.execute(query, data)

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
    item = get_item(item_id)

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

    filename = str(item_id)
    print(filename)

    return render_template('item.html', item=item, ratings=reviews, filename = filename)


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

            query = "SELECT MAX(i.id) FROM item i;"
            cursor.execute(query)
            item_id = None
            for (result, ) in cursor:
                item_id = result

            if 'file' in request.files:
                f = request.files['file']
                if f and allowed_file(f.filename):
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], str(item_id)))

            query = "SELECT COUNT(*) FROM featuredItem;"
            cursor.execute(query)
            num = None
            for (result, ) in cursor:
                num = result
            if num >= 8:
                query = "DELETE FROM featuredItem ORDER BY id ASC LIMIT 1;"
                cursor.execute(query)

            query = "INSERT INTO featuredItem (itemId) VALUES (%s);"
            data = (item_id, )
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


@app.route('/review/<int:item_id>', methods=['GET', 'POST'])
@requires_log_in
def review(item_id):
    error = None

    cnx = get_connector()
    cursor = cnx.cursor()

    if request.method == 'POST':

        try:
            rating = int(request.form['rating'])
            if rating > 5 or rating < 1:
                raise ValueError
            description = request.form['description']

            query = "INSERT INTO review (itemId, userId, rating, description) VALUES (%s, %s, %s, %s);"
            data = (item_id, session['user_id'], rating, description)
            cursor.execute(query, data)

            cnx.commit()

            cnx.close()

            return redirect(url_for('item_page', item_id=item_id))

        except ValueError:
            error = 'Please enter a valid number for the rating, between 1 and 5 inclusive.'

    cnx.close()

    return render_template('give_review.html', error=error)


class Purchase:
        def __init__(self, item_id, item, date, price, seller, quantity):
            self.item_id = item_id
            self.item = item
            self.date = date
            self.price = price
            self.seller = seller
            self.quantity = quantity


@app.route('/order_history', methods=['GET', 'POST'])
@requires_log_in
def order_history():
    error = None

    user_id = session['user_id']

    cnx = get_connector()
    cursor = cnx.cursor()

    query = 'SELECT i.id, i.name, p.purchaseDate, i.price, u.email_address, t.quantity FROM item i, takenItem t, purchase p, person u WHERE p.buyerId = %s AND i.id = t.itemId AND p.cartId = t.cartID AND u.id = i.seller_id ORDER BY p.purchaseDate DESC;'
    data = (user_id, )
    cursor.execute(query, data)

    purchases = []
    for (item_id, item_name, purchase_date, price, email_address, quantity) in cursor:
        purchases.append(Purchase(item_id, item_name, purchase_date, price, email_address, quantity))

    cnx.close()

    return render_template('order_history.html', error=error, purchases=purchases)


@app.route('/inventory', methods=['GET', 'POST'])
@requires_log_in
def inventory():
    error = None
    user_id = session['user_id']
    cnx = get_connector()
    cursor = cnx.cursor()

    # Get all the items that are sold by the current user
    query = ('SELECT i.id, i.name, i.description, i.price, i.quantity, c.name '
             'FROM item i, category c '
             'WHERE i.seller_id = %s AND c.id = i.category_id')
    data = (user_id, )
    cursor.execute(query, data)

    inventory = []
    for (item_id, name, desc, price, quantity, category) in cursor:
        inventory.append(Item(item_id, name, desc, price, None, quantity, category))

    cnx.close()

    return render_template('inventory.html', error=error, items=inventory)


@app.route('/listing/<int:item_id>', methods=['GET', 'POST'])
@requires_log_in
def edit_listing(item_id):
    error = None
    user_id = session['user_id']
    cnx = get_connector()
    cursor = cnx.cursor()

    query = 'SELECT i.seller_id FROM item i where i.id = %s'
    data = (item_id, )
    cursor.execute(query, data)

    seller_id = (cursor.fetchone())[0]

    # If the user isn't the items seller, take us away
    if seller_id != user_id:
        return redirect(url_for('index'))

    item = get_item(item_id)

    query = 'SELECT c.name FROM category c;'
    cursor.execute(query)

    categories = []
    for (category, ) in cursor:
        categories.append(category)

    #TODO FINISH THE EDIT LISTING LOGIC! Preferably that will go in another function if possible

    return render_template('edit_listing.html', error=error, item=item, categories=categories)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
