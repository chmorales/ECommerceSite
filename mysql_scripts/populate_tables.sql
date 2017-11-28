USE CSE305;

INSERT INTO address (streetNumber, streetName, city, zipCode, country) VALUES
    (5, "Somerset Drive", "Holbrook", "11741", "USA");

INSERT INTO cart (price) VALUES
    (0.0),
    (0.0),
    (0.0),
    (0.0);

INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES
    ("Bob", "Admin", "pa", "B.Admin@gmail.com", 1),
    ("Anthony", "Mulieri", "password", "amulieri@gmail.com", 2),
    ("Chris", "Morales", "password", "cmorales@gmail.com", 3),
    ("Daniel", "Shank", "password", "dshank@gmail.com", 4);

INSERT INTO administrator (userId) VALUES
    (1);

INSERT INTO category (name, description) VALUES
    ("Electronics", "Electric Things"), 
    ("Animals", "cute animals"),
    ("People", "Slaves!"),
    ("Drugs", "Chris's Favorite Section"),
    ("Clothing", "warmy bois");

INSERT INTO item (name, description, price, seller_id, quantity, category_id) VALUES
    ("TV", "a TV", 56.66, 1, 2, 1),
    ("Toaster", "Toasty", 3.33, 2, 1, 1),
    ("Meth", "1 meth", 62.32, 2, 1, 4),
    ("Dog", "a heckin cute pupper!", 4.42, 2, 3, 2),
    ("Sean", "Sean Milligan", .02, 2, 1, 3);

/* We don't want to insert any purchases yet. */
/* We don't want to insert any taken items yet. */

INSERT INTO review (itemId, userId, rating, description) VALUES
    (1, 1, 5, "A great tv wow.");
