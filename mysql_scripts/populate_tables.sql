USE CSE305;

INSERT INTO address (streetNumber, streetName, city, zipCode, country) VALUES
    (5, "Somerset Drive", "Holbrook", "11741", "USA");

INSERT INTO cart (price) VALUES
    (0.0),
    (0.0),
    (0.0),
    (0.0);

INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES
    ("Bob", "Admin", "$5$rounds=535000$GEv87LSEvPTt1hu9$59ZMft5A7vLu.kClsqQqEq9GHMMU2tj85MXy.JFkAa0", "B.Admin@gmail.com", 1),
    ("Robert", "Mulieri", "$5$rounds=535000$22gPXxvTeOeqxn4L$YG.2B87TeOWmq4GAbQ066Ga.rhMf56hD.QNQLX5t1H3", "amulieri@gmail.com", 2),
    ("Chris", "Morales", "$5$rounds=535000$nhFyR.sl5IF8EzLh$5/HVRAZigxaEiEze2MIqMZ1fADvEajbEdZqIW59D.M3", "cmorales@gmail.com", 3),
    ("Daniel", "Shank", "$5$rounds=535000$iW8iQnCu0JcnTlXU$69D2XgYMreeiCRTfvgnqnmDCBs/OuPoCbSSStAGd4t5", "dshank@gmail.com", 4);

INSERT INTO administrator (userId) VALUES
    (1);

INSERT INTO category (name, description) VALUES
    ("Electronics", "Electric Things"), 
    ("Animals", "cute animals"),
    ("People", "Slaves!"),
    ("Drugs", "Chris's Favorite Section"),
    ("Clothing", "warmy bois");

INSERT INTO item (name, description, price, seller_id, quantity, category_id, reference) VALUES
    ("TV", "a TV", 56.66, 1, 2, 1, 1),
    ("Toaster", "Toasty", 3.33, 2, 1, 1, 2),
    ("Meth", "1 meth", 62.32, 2, 1, 4, 3),
    ("Dog", "a heckin cute pupper!", 4.42, 2, 3, 2, 4),
    ("Sean", "Sean Milligan", .02, 2, 1, 3, 5),
    ("Generic Item", "A generic item for sale", 0.99, 4, 99, 4, 6);

/* We don't want to insert any purchases yet. */
/* We don't want to insert any taken items yet. */

INSERT INTO review (itemId, userId, rating, description) VALUES
    (1, 1, 5, "A great tv wow."),
    (1, 2, 3, "It's alright at best."),
    (2, 1, 2, "Doesn't work in bathtub."),
    (1, 3, 4, "Helps me sleep at night.");

INSERT INTO featuredItem (itemId) SELECT i.id FROM item i LIMIT 10;

INSERT INTO message (message, recipientId, sender ) VALUES 
    ("This is a test message.", 2, "SYSTEM"),
    ("This is another test message.", 2, "SYSTEM"),
    ("This is a message from another user.", 2, "B.Admin@gmail.com"),
    ("This is a reply to a user.", 1, "amulieri@gmail.com"),
    ("This is another reply to a user.", 2, "B.Admin@gmail.com");
