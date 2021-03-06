from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for
from passlib.hash import sha256_crypt
import pymysql
from db_connector import get_connector
from functools import wraps
import os

UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


class Item:
    def __init__(self, item_id, name, description, price, seller, quantity,
                 category, image_link):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.price = price
        self.seller = seller
        self.quantity = quantity
        self.category = category
        self.image_link = image_link
        self.total_price = None
        if self.price is not None and self.quantity is not None:
            self.total_price = self.price * self.quantity


class Review:
    def __init__(self, rating, description, item_id, first_name, last_name, item_name=None):
        self.rating = rating
        self.description = description
        self.item_id = item_id
        self.first_name = first_name
        self.last_name = last_name
        self.item_name = item_name


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
        last_name = None
        if 'user_id' in session:
            user_id = session['user_id']
            first_name = session['first_name']
            last_name = session['last_name']
            logged_in = True

        kwargs['user_id'] = user_id
        kwargs['logged_in'] = logged_in
        kwargs['first_name'] = first_name
        kwargs['last_name'] = last_name
        return func(*args, **kwargs)
    return temp_with_user_id


# Redefines render_template to inlude user_id and logged_in variables
render_template = user_id_decorator(render_template)


def get_item(cnx, cursor, item_id):
    query = 'SELECT i.name, i.description, i.price, i.quantity, s.email_address, c.name, i.imageLink FROM item i, person s, category c WHERE i.id = %s AND i.category_id = c.id AND i.seller_id = s.id;'
    data = (item_id, )
    cursor.execute(query, data)
    item = None
    for (name, description, price, quantity, email_address, category_name, image_link) in cursor:
        item = Item(item_id, name, description, price, email_address, quantity, category_name, image_link)
    return item


def get_categories():
    cnx = get_connector()
    cursor = cnx.cursor()
    query = 'SELECT c.name FROM category c ORDER BY c.name;'
    cursor.execute(query)
    categories = []
    for (result, ) in cursor:
        categories.append(result)
    categories.insert(0, 'All')
    cnx.close()
    return categories


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def index():
    cnx = get_connector()
    cursor = cnx.cursor()
    query = ("SELECT itemId FROM featuredItem;")
    cursor.execute(query)

    items = []
    cnx2 = get_connector()
    cursor2 = cnx2.cursor()
    for (item_id, ) in cursor:
        items.append(get_item(cnx2, cursor2, item_id))
    return render_template('homepage.html', items=items, categories=get_categories())

class PasswordError(Exception):
    pass


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

            # # Using prepared statements to prevent SQL injection
            # query = ("SELECT u.first_name, u.last_name, u.id FROM person u WHERE u.email_address = %s AND u.password = %s;")
            # data = (email, password)
            # cursor.execute(query, data)

            # for (first_name, last_name, user_id) in cursor:
            #     session['user_id'] = user_id
            #     session['first_name'] = first_name
            #     session['last_name'] = last_name
            #     return redirect(url_for('index'))
            # error = 'Invalid email and password combonation.'
            # return render_template('login.html', error=error, create_error=create_error, categories=get_categories())

            # Query for person matching givin email
            query = ("SELECT u.first_name, u.last_name, u.id, u.password FROM person u WHERE u.email_address = %s;")
            data = (email)
            cursor.execute(query, data)

            # Verify password hash
            for (first_name, last_name, user_id, password_hash) in cursor:
                if not sha256_crypt.verify(password, password_hash):
                    break
                session['user_id'] = user_id
                session['first_name'] = first_name
                session['last_name'] = last_name
                return redirect(url_for('index'))
            error = 'Invalid email and password combonation.'
            return render_template('login.html', error=error, create_error=create_error, categories=get_categories())

        elif 'create_account' in request.form:
            cnx = get_connector()
            cnx.begin()
            cursor = cnx.cursor()

            # We need the email address, password, firstname, and lastname.
            email_address = request.form['create_email']
            password = request.form['create_password']
            first_name = request.form['create_first_name']
            last_name = request.form['create_last_name']

            try:
                if len(password) < 8:
                    raise PasswordError

                # Create a new cart just for our user.
                query = 'INSERT INTO cart (price) VALUES (%f);' % (0.0)
                cursor.execute(query)

                # Password hashing
                password = sha256_crypt.hash(password)

                # Insert the new user into the database.
                query = 'INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES (%s, %s, %s, %s, LAST_INSERT_ID());'
                data = (first_name, last_name, password, email_address)
                cursor.execute(query, data)

                # Save the userId into the session.
                query = 'SELECT MAX(id) FROM person;'
                cursor.execute(query)
                user_id = int(cursor.fetchone()[0])
                session['user_id'] = user_id
                session['first_name'] = first_name
                session['last_name'] = last_name

                # Commit, close, and redirect.
                cnx.commit()
                cnx.close()
                return redirect(url_for('index'))

            except pymysql.err.IntegrityError:
                # Should only fire if the email address already exists in the database.
                create_error = 'That email is already taken. Please try a new email.'
                cnx.rollback()
                cnx.close()
                return render_template('login.html', error=error, create_error=create_error, categories=get_categories())
            except PasswordError:
                create_error = 'Passwords must be 8 characters long or greater.'
                cnx.rollback()
                cnx.close()
                return render_template('login.html', error=error, create_error=create_error, categories=get_categories())

        cnx.close()
    return render_template('login.html', error=error, create_error=create_error, categories=get_categories())


@app.route('/logout')
@requires_log_in
def logout():
    session.pop('user_id', None)
    session.pop('first_name', None)
    session.pop('last_name', None)
    session['logged_in'] = False
    return redirect(url_for('index'))


# You should be able to see order history, your reviews, and items you're selling
@app.route('/profile', methods=['GET', 'POST'])
@requires_log_in
def profile():
    user_id = session['user_id']

    # Get reviews that the user had posted
    cnx = get_connector()
    cursor = cnx.cursor()
    
    if request.method == 'POST':
        if 'delete' in request.form:
            query = 'UPDATE message SET unread = FALSE WHERE recipientId = %s AND id = %s;'
            data = (user_id, request.form['id'])
            cursor.execute(query, data)
            cnx.commit()
        if 'reply' in request.form:
            return redirect(url_for('message', other_id = request.form['id']))

    query = ('SELECT r.rating, r.description, r.itemId, r.userId FROM review r WHERE r.userId = %s;')
    data = (session['user_id'], )
    cursor.execute(query, data)

    # Geting building list of reviews and list of item names, hopefully in same order
    reviews = []
    for (rating, description, item_id, user_id) in cursor:
        item_cursor = cnx.cursor()
        query = ('SELECT i.name FROM item i WHERE i.id = %s;')
        data = (item_id, )
        item_cursor.execute(query, data)
        for (item_name) in item_cursor:
            reviews.append(Review(rating, description, item_id, session['first_name'], session['last_name'], item_name[0]))

    query = ('SELECT i.id, i.name, p.purchaseDate, i.price, u.email_address, t.quantity, i.reference '
             'FROM item i, takenItem t, purchase p, person u '
             'WHERE p.buyerId = %s AND i.id = t.itemId AND p.cartId = t.cartID AND u.id = i.seller_id '
             'ORDER BY p.purchaseDate DESC;')
    data = (user_id, )
    cursor.execute(query, data)

    purchases = []
    for (item_id, item_name, purchase_date, price, email_address, quantity, reference) in cursor:
        purchases.append(Purchase(item_id, item_name, purchase_date, price, email_address, quantity, reference))

    messages = []
    query = 'SELECT m.id, m.message, m.sender FROM message m WHERE m.recipientId = %s AND m.unread = TRUE;'
    data = (user_id, )
    cursor.execute(query, data)
    for (result1, result2, result3) in cursor:
        messages.append((result1, result2, result3))

    cnx.close()

    return render_template('profile.html', reviews=reviews, purchases=purchases, messages=messages, categories=get_categories())


@app.route("/message/<int:other_id>", methods=['POST', 'GET'])
@requires_log_in
def message(other_id):
    cnx = get_connector()
    cursor = cnx.cursor()
    user_id = session['user_id']
        
    query = 'SELECT p.email_address FROM person p WHERE p.id = %s;'
    data = (user_id, )
    cursor.execute(query, data)
    user_email = None
    for (result, ) in cursor:
        user_email = result

    query = 'SELECT p.id, p.email_address FROM person p, message m WHERE m.sender = p.email_address;'
    cursor.execute(query)
    other_id = None
    other_email = None
    for (result1, result2) in cursor:
        other_id = result1
        other_email = result2

    if request.method == 'POST':
        query = 'INSERT INTO message (message, recipientId, sender) VALUES (%s, %s, %s);'
        data = (request.form['message'], other_id, user_email)
        cursor.execute(query, data)

        cnx.commit()

    query = 'SELECT m.sender, m.message, m.id, m.recipientId FROM message m WHERE m.recipientId = %s AND m.sender = %s OR m.recipientId = %s AND m.sender = %s ORDER BY m.id ASC;'
    data = (user_id, other_email, other_id, user_email)
    cursor.execute(query, data)
    messages = []
    for (result1, result2, result3, result4) in cursor:
        c = 't' if result4 == user_id else 'f'
        messages.append((result1, result2, c))

    cnx.close()

    return render_template('message.html', messages=messages, categories=get_categories())


@app.route("/message_user/<int:other_id>", methods=['POST', 'GET'])
@requires_log_in
def message_user(other_id):
    cnx = get_connector()
    cursor = cnx.cursor()
    user_id = session['user_id']
        
    query = 'SELECT p.email_address FROM person p WHERE p.id = %s;'
    data = (user_id, )
    cursor.execute(query, data)
    user_email = None
    for (result, ) in cursor:
        user_email = result

    query = 'SELECT p.email_address FROM person p WHERE p.id = %s;'
    data = (other_id, )
    cursor.execute(query, data)
    other_email = None
    for (result, ) in cursor:
        other_email = result

    if request.method == 'POST':
        query = 'INSERT INTO message (message, recipientId, sender) VALUES (%s, %s, %s);'
        data = (request.form['message'], other_id, user_email)
        cursor.execute(query, data)

        cnx.commit()

    query = 'SELECT m.sender, m.message, m.id, m.recipientId FROM message m WHERE m.recipientId = %s AND m.sender = %s OR m.recipientId = %s AND m.sender = %s ORDER BY m.id ASC;'
    data = (user_id, other_email, other_id, user_email)
    cursor.execute(query, data)
    messages = []
    for (result1, result2, result3, result4) in cursor:
        c = 't' if result4 == user_id else 'f'
        messages.append((result1, result2, c))

    cnx.close()

    return render_template('message.html', messages=messages, categories=get_categories())


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
        user_id = session['user_id']

        # Get the current user's cartId.
        query = 'SELECT p.cartId FROM person p WHERE p.id = %s;'
        data = (user_id, )
        cursor.execute(query, data)
        cart_id = None
        for (result, ) in cursor:
            cart_id = result

        query = ("SELECT * "
                 "FROM takenItem t INNER JOIN cart c ON t.cartId = c.id "
                 "WHERE c.id = %s")
        data = (cart_id, )
        empty = True
        cursor.execute(query, data)

        for item in cursor:
            empty = False

        if empty:
            cnx.commit()
            cnx.close()
            return redirect(url_for('shopping_cart'))

        return redirect(url_for('checkout'))

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
        cart_price = round(result, 2)

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
            items.append(Item(item_id, name, description, price, email_address, quantities[item_id], None, None))

    return render_template('cart.html', items=items, cart_price=cart_price, categories=get_categories())


@app.route("/cart/remove/<int:item_id>", methods=['POST'])
@requires_log_in
def remove_from_cart(item_id):
    user_id = session['user_id']
    cnx = get_connector()
    cursor = cnx.cursor()

    # Getting the users cart id
    query = "SELECT p.cartId FROM person p WHERE p.id = %s FOR UPDATE;"
    data = (user_id, )
    cursor.execute(query, data)
    cart_id = None
    for (cart, ) in cursor:
        cart_id = cart

    # Update the item listing to have one more
    query = "UPDATE item SET quantity = quantity + 1 WHERE id = %s;"
    data = (item_id, )
    cursor.execute(query, data)

    # Reduce the total price of the cart
    query = ('UPDATE cart c, item i '
             'SET c.price = c.price - i.price '
             'WHERE i.id = %s AND c.id = %s;')
    data = (item_id, cart_id)
    cursor.execute(query, data)
    # Note that we use the same data for the remaining queries

    # Reduce the quantity in the cart by one
    query = ("UPDATE takenItem t "
             "SET t.quantity = t.quantity - 1 "
             "WHERE itemId = %s AND cartId = %s;")
    cursor.execute(query, data)

    # If there are no more of the item in the cart, remove it from the cart
    query = ("DELETE FROM takenItem "
             "WHERE itemId = %s AND cartId = %s AND quantity = 0;")
    cursor.execute(query, data)

    cnx.commit()
    cnx.close()

    return redirect(url_for('shopping_cart'))


@app.route("/hello")
def hello():
    return render_template('test.html', categories=get_categories())


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        search_string = request.form['search_input']
        category_name = request.form['search_category']
        return redirect(url_for('search_results', string=search_string, category_name = category_name))


@app.route('/search/<string:string>/<string:category_name>', methods=['GET', 'POST'])
def search_results(string, category_name):
    if request.method == 'POST':
        search_string = request.form['search_input']
        category_name = request.form['search_category']
        return redirect(url_for('search_results', string=search_string, category_name = category_name))

    # Get the database connection.
    cnx = get_connector()
    cursor = cnx.cursor()

    print(request.form)

    if category_name == 'All':
        # Search for any items with a name containing the search string.
        query = ('SELECT i.id, i.name, i.description, i.price, i.quantity '
                'FROM item i '
                'WHERE i.name LIKE %s AND i.listed;')
        data = ('%' + string + '%', )
    else:
        query = 'SELECT i.id, i.name, i.description, i.price, i.quantity FROM item i, category c WHERE i.category_id = c.id AND c.name = %s AND i.name LIKE %s AND i.listed;'
        data = (category_name, '%' + string + '%')
    
    cursor.execute(query, data)

    # Save the results into a list of items.
    items = []
    for (item_id, name, description, price, quantity) in cursor:
        items.append(Item(item_id, name, description, price, None, quantity, None, None))

    cnx.close()
    return render_template('search_results.html', items=items, search_string=string, categories=get_categories())


@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item_page(item_id):
    # Gets database connection.
    cnx = get_connector()
    cursor = cnx.cursor()

    # Gets relevant information from item table.
    query = 'SELECT i.seller_id FROM item i WHERE i.id = %s;'
    data = (item_id, )
    cursor.execute(query, data)
    seller_id = None
    for (result, ) in cursor:
        seller_id = result

    if request.method == 'POST':

        if 'message_vendor' in request.form:
            return redirect(url_for('message_user', other_id=seller_id))

        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_id = session['user_id']

        query = 'SELECT i.quantity, i.price FROM item i WHERE i.id = %s;'
        data = (item_id, )
        cursor.execute(query, data)
        num = None
        price = None
        for (result, result2 ) in cursor:
            num = result
            price = result2

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

            query = 'UPDATE cart SET price = price + %s WHERE id = %s;'
            data = (price, cart_id)
            cursor.execute(query, data)

            exists = False
            query = 'SELECT i.itemId FROM takenItem i, person p WHERE i.itemId = %s AND i.cartId = p.cartId AND p.id = %s;'
            data = (item_id, user_id)
            cursor.execute(query, data)
            for item in cursor:
                exists = True

            if exists:
                query = 'UPDATE takenItem t, person p SET t.quantity = t.quantity + 1 WHERE t.itemId = %s AND t.cartId = p.cartId AND p.id = %s;'
                data = (item_id, user_id)
                cursor.execute(query, data)

            if not exists:
                query = 'INSERT INTO takenItem (itemId, cartId, quantity) VALUES (%s, %s, %s);'
                data = (item_id, cart_id, 1)
                cursor.execute(query, data)

        cnx.commit()

    # Walks through result, setting up object.
    item = get_item(cnx, cursor, item_id)

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
        reviews.append(Review(rating, description, item_id, fn, ln))
        cnx2.close()
    cnx.close()

    if item.image_link is None:
        f = 'miss_img'
    else:
        f = item.image_link
    filename = url_for('static', filename=f)

    return render_template('item.html', item=item, ratings=reviews, filename=filename, vendor_id=seller_id, categories=get_categories())


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

            query = "SELECT MAX(i.id) FROM item i;"
            cursor.execute(query)
            item_id = None
            for (result, ) in cursor:
                item_id = result + 1

            uploaded = False
            if 'file' in request.files:
                f = request.files['file']
                if f and allowed_file(f.filename):
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], str(item_id)))
                    uploaded = True

            query = 'SELECT c.id FROM category c WHERE c.name = %s'
            data = (category_name, )
            cursor.execute(query, data)
            category_id = None
            for (category_id_result, ) in cursor:
                category_id = category_id_result

            if not uploaded:
                query = "INSERT INTO item (name, description, price, seller_id, quantity, category_id, reference) VALUES (%s, %s, %s, %s, %s, %s, 0)"
                data = (name, description, price, session['user_id'], quantity, category_id)
            else:
                query = "INSERT INTO item (name, description, price, seller_id, quantity, category_id, reference, imageLink) VALUES (%s, %s, %s, %s, %s, %s, 0, %s)"
                data = (name, description, price, session['user_id'], quantity, category_id, item_id)
            cursor.execute(query, data)

            query = "UPDATE item i SET i.reference = LAST_INSERT_ID() WHERE i.id = LAST_INSERT_ID();"
            cursor.execute(query)

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

            return redirect(url_for('item_page', item_id=item_id))

        except ValueError:
            error = 'Please enter valid numbers for the quantity and price.'

    query = 'SELECT c.name FROM category c;'
    cursor.execute(query)

    categories = []
    for (category, ) in cursor:
        categories.append(category)

    cnx.close()

    return render_template('sell_item.html', error=error, categories2=categories, categories=get_categories())


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

    item = get_item(cnx, cursor, item_id)

    cnx.close()

    return render_template('leave_review.html', error=error, item=item, categories=get_categories())


class Purchase:
        def __init__(self, item_id, item, date, price, seller, quantity, reference=None):
            self.item_id = item_id
            self.item = item
            self.date = date
            self.price = price
            self.seller = seller
            self.quantity = quantity
            self.reference = reference


# @app.route('/order_history', methods=['GET', 'POST'])
# @requires_log_in
# def order_history():
#     error = None
#
#     user_id = session['user_id']
#
#     cnx = get_connector()
#     cursor = cnx.cursor()
#
#     query = ('SELECT i.id, i.name, p.purchaseDate, i.price, u.email_address, t.quantity '
#              'FROM item i, takenItem t, purchase p, person u '
#              'WHERE p.buyerId = %s AND i.id = t.itemId AND p.cartId = t.cartID AND u.id = i.seller_id '
#              'ORDER BY p.purchaseDate DESC;')
#     data = (user_id, )
#     cursor.execute(query, data)
#
#     purchases = []
#     for (item_id, item_name, purchase_date, price, email_address, quantity) in cursor:
#         purchases.append(Purchase(item_id, item_name, purchase_date, price, email_address, quantity))
#
#     cnx.close()
#
#     return render_template('order_history.html', error=error, purchases=purchases)


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
             'WHERE i.seller_id = %s AND c.id = i.category_id AND i.listed;')
    data = (user_id, )
    cursor.execute(query, data)

    inventory = []
    for (item_id, name, desc, price, quantity, category) in cursor:
        inventory.append(Item(item_id, name, desc, price, None, quantity, category, None))

    cnx.close()

    return render_template('inventory.html', error=error, items=inventory, categories=get_categories())


@app.route('/listing/<int:item_id>', methods=['GET', 'POST'])
@requires_log_in
def listing(item_id):
    error = None
    user_id = session['user_id']
    cnx = get_connector()
    cursor = cnx.cursor()

    query = 'SELECT i.seller_id, i.listed FROM item i where i.id = %s'
    data = (item_id, )
    cursor.execute(query, data)

    (seller_id, listed) = cursor.fetchone()

    # If the user isn't the items seller, take us away
    if seller_id != user_id or not listed:
        return redirect(url_for('inventory'))

    if request.method == 'POST':
        old_item = get_item(cnx, cursor, item_id)

        query = 'SELECT p.id FROM person p, takenItem i, cart c WHERE i.itemId = %s AND i.cartId = c.id AND c.id = p.cartId;'
        data = (old_item.item_id, )
        cursor.execute(query, data)
        users = []
        for (result, ) in cursor:
            users.append(result)

        if 'edit' in request.form:
            try:
                for user in users:
                    query = 'INSERT INTO message (message, recipientId, sender) VALUES (%s, %s, %s);'
                    msg = 'The listing for ' + old_item.name + ' has been updated.'
                    data = (msg, user, 'SYSTEM')
                    cursor.execute(query, data)

                cnx.commit()
                cnx.close()

                return edit_listing(item_id)
            except ValueError:
                error = "Please input valid numbers for the quantity and price"
        if 'remove' in request.form:
            for user in users:
                query = 'INSERT INTO message (message, recipientId, sender) VALUES (%s, %s, %s);'
                msg = 'The listing for ' + old_item.name + ' has been removed.'
                data = (msg, user, 'SYSTEM')
                cursor.execute(query, data)

            cnx.commit()
            cnx.close()

            return remove_listing(item_id)

    item = get_item(cnx, cursor, item_id)

    query = 'SELECT c.name FROM category c;'
    cursor.execute(query)

    categories = []
    for (category, ) in cursor:
        categories.append(category)

    cnx.close()

    return render_template('listing.html', error=error, item=item,
                           categories2=categories, categories=get_categories())


def edit_listing(item_id):
    """ Edit Listing transaction """
    cnx = get_connector()
    cursor = cnx.cursor()

    # Get the new values
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    category_name = request.form['category']

    old_item = get_item(cnx, cursor, item_id)

    # If only the quantity has changed, we update the quantity of the item
    if (old_item.name == name and old_item.description == description and
            old_item.price == price and
            old_item.category == category_name):
        cnx.begin()
        query = 'UPDATE item i SET i.quantity = %s WHERE i.id = %s'
        data = (quantity, item_id)

        cursor.execute(query, data)
    # Otherwise we make a new item and update the whole database
    else:
        cnx.begin()
        # Get the category id of selected category
        query = 'SELECT c.id FROM category c WHERE c.name = %s FOR UPDATE'
        data = (category_name, )
        cursor.execute(query, data)
        category_id = None
        for (category_id_result, ) in cursor:
            category_id = category_id_result

        # Create the new item to replace the old item
        query = 'INSERT INTO item (name, description, price, seller_id, quantity, category_id, reference) VALUES (%s, %s, %s, %s, %s, %s, %s);'
        data = (name, description, price, session['user_id'], quantity, category_id, item_id)
        cursor.execute(query, data)

        if old_item.image_link != None:
            query = 'UPDATE item SET imageLink = %s WHERE reference = %s;'
            data = (old_item.image_link, item_id)
            cursor.execute(query, data)

        # We use the old item id for the next several queries
        data = (old_item.item_id, )

        # Change the old item to be unlisted
        query = 'UPDATE item i SET i.listed = FALSE WHERE i.id = %s;'
        cursor.execute(query, data)

        # Update the references to point to the new item
        query = 'UPDATE item i SET i.reference = LAST_INSERT_ID() WHERE i.reference = %s;'
        cursor.execute(query, data)

        # Update the reviews to point the new listing
        query = 'UPDATE review r SET r.itemId = LAST_INSERT_ID() WHERE r.itemId = %s;'
        cursor.execute(query, data)

        # If the item is on the featured items table, update it to point to the new listing
        query = 'UPDATE featuredItem f SET f.itemId = LAST_INSERT_ID() WHERE f.itemId = %s;'
        cursor.execute(query, data)

        # Updates taken items in carts that are still in use to point to the new listing.
        query = ('UPDATE takenItem t, cart c, person p '
                 'SET t.itemId = LAST_INSERT_ID() '
                 'WHERE t.itemId = %s AND t.cartId = c.id AND c.id = p.cartId;'
                 )
        cursor.execute(query, data)

        # Update cart prices to reflect the new price of the item
        query = ('UPDATE cart c, takenItem t, person p '
                 'SET c.price = c.price + (t.quantity * (%s - %s)) '
                 'WHERE t.itemId = LAST_INSERT_ID() AND t.cartId = c.id AND c.id = p.cartId;'
                 )
        data = (price, old_item.price)
        cursor.execute(query, data)

    cnx.commit()
    cnx.close()

    return redirect(url_for('inventory'))


def remove_listing(item_id):
    """ Remove listing transaction """
    cnx = get_connector()
    cnx.begin()
    cursor = cnx.cursor()
    data = (item_id, )

    # Set the item to unlisted
    query = 'UPDATE item i SET i.listed = FALSE, i.quantity = 0 WHERE i.id = %s;'
    cursor.execute(query, data)

    # Reduce the price of carts with the item
    query = ('UPDATE cart c, takenItem t, item i '
             'SET c.price = c.price - (t.quantity * i.price) '
             'WHERE t.itemId = i.id AND t.cartId = c.id AND i.id = %s;')
    cursor.execute(query, data)

    # Remove the item from carts which contain it
    query = 'DELETE FROM takenItem WHERE itemId = %s;'
    cursor.execute(query, data)

    # Remove the item from the featured items table
    query = 'DELETE FROM featuredItem WHERE itemId = %s;'
    cursor.execute(query, data)

    # Commit the transaction
    cnx.commit()
    cnx.close()
    return redirect(url_for('inventory'))

@app.route('/checkout', methods=['GET', 'POST'])
@requires_log_in
def checkout():

    if request.method == 'POST':

        cnx = get_connector()
        cursor = cnx.cursor()

        user_id = session['user_id']

        # Get the current user's cartId.
        query = 'SELECT p.cartId FROM person p WHERE p.id = %s;'
        data = (user_id, )
        cursor.execute(query, data)
        cart_id = None
        for (result, ) in cursor:
            cart_id = result

        query = ("SELECT * "
                 "FROM takenItem t INNER JOIN cart c ON t.cartId = c.id "
                 "WHERE c.id = %s FOR UPDATE")
        data = (cart_id, )
        empty = True
        cursor.execute(query, data)

        for item in cursor:
            empty = False

        if empty:
            cnx.commit()
            cnx.close()
            return redirect(url_for('shopping_cart'))

        query = 'INSERT INTO cart (price) VALUES (%f);' % (0.0)
        cursor.execute(query)

        # Update the user's cart to that one.
        query = 'UPDATE person SET cartId = LAST_INSERT_ID();'
        cursor.execute(query)

        # Put the old cart into a saved purchase slot.
        query = 'INSERT INTO purchase (buyerId, cartId, purchaseDate) VALUES (%s, %s, NOW());'
        data = (user_id, cart_id)
        cursor.execute(query, data)

        cnx.commit()
        cnx.close()

        return redirect(url_for('shopping_cart'))
    
    # Get a list of states from the 'static/states.txt' file.
    states = []
    for line in open('static/states.txt', 'r'):
        states.append(line)

    # Get a list of states from the 'static/card_types.txt' file.
    card_types = []
    for line in open('static/card_types.txt', 'r'):
        card_types.append(line)

    return render_template("checkout.html", states=states, card_types=card_types, categories=get_categories())

@app.route('/all')
def all():
    cnx = get_connector()
    cursor = cnx.cursor()

    query = 'SELECT id, name, description, price, quantity FROM item WHERE id = reference AND listed ORDER BY name ASC;'
    cursor.execute(query)
    items = []
    for (item_id, name, description, price, quantity) in cursor:
        items.append(Item(item_id, name, description, price, None, quantity, None, None))
    
    cnx.close()
    return render_template('all.html', items=items, categories=get_categories())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
