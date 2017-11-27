USE CSE305;

INSERT INTO address (streetNumber, streetName, city, zipCode, country) VALUES
    (5, "Somerset Drive", "Holbrook", "11741", "USA");

INSERT INTO cart (price) VALUES
    (0.0),
    (0.0);

INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES
    ("Bob", "Admin", "pa", "B.Admin@gmail.com", 1),
    ("Anthony", "Mulieri", "pa", "amulieri@gmail.com", 2);

INSERT INTO administrator (userId) VALUES
    (1);

INSERT INTO category (name, description) VALUES
    ("Electronics", "Electric Things"), 
    ("Drugs", "Chris's Favorite Section");

INSERT INTO item (name, description, price, seller_id, quantity, category_id) VALUES
    ("TV", "a TV", 56.66, 1, 2, 1),
    ("Toaster", "Toasty", 3.33, 2, 1, 1),
    ("Meth", "1 meth", 62.32, 2, 1, 2);

/* We don't want to insert any purchases yet. */
/* We don't want to insert any taken items yet. */

INSERT INTO review (itemId, userId, rating, description) VALUES
    (1, 1, 5, "A great tv wow.");
