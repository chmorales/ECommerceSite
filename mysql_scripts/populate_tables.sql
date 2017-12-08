USE CSE305;

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
    /* 1 */
    ("Electronics", "Items utilizing electricity."), 
    /* 2 */
    ("Food", "Edible items."),
    /* 3 */
    ("Outdoors", "Camping equipement."),
    /* 4 */
    ("Games", "Whether video or board."),
    /* 5 */
    ("Books", "Spreading knowledge through reading."),
    /* 6 */
    ("Clothing", "Stuff you wear.");

INSERT INTO item (name, description, price, seller_id, quantity, category_id) VALUES
    ("Toaster", "Warms bread and other bread items.", 60.11, 1, 3, 1),
    ("Microwave", "Warms items that you put inside for any amount of time.", 45.23, 1, 11, 1),
    ("Television", "70 inch 3D television, guaranteed to completely destroy your eyes.", 5000, 1, 1, 1),
    ("Coca-Cola", "A delicious can of coke.", 2.99, 2, 100, 2),
    ("Grapes", "A bundle of 5-8 grapes.", 5.66, 3, 57, 2),
    ("Bananas", "A bundle of 6-7 bananas.", 3.33, 3, 24, 2),
    ("Log", "A single log, used for making fires.", 23.66, 4, 5, 3),
    ("Tent", "A tent to keep you and the whole family warm.", 15.66, 4, 11, 3),
    ("Hammock", "A hammock to lay on.", 13.33, 4, 17, 3),
    ("Battlefront 2", "The horrible EA remake.", 2.22, 1, 1000, 4),
    ("Chutes and Ladders", "A game of wit and deception.", 13.22, 1, 33, 4),
    ("Overwatch", "The cult-classic.", 40, 1, 14, 4),
    ("War and Peace", "A classic long-winded novel.", 15, 2, 5, 5),
    ("Green Eggs and Ham", "The classic Dr. Seuss story.", 15, 2, 5, 5),
    ("A Game of Thrones", "The first book in George R.R. Martin's fantasy series.", 15, 2, 5, 5),
    ("Hat", "A hat.", 16, 3, 15, 6),
    ("Shorts", "A pair of okay shorts.", 23.15, 3, 25, 6),
    ("Shirt", "A lousy ole' shirt.", 19.27, 3, 11, 6);

/* We don't want to insert any purchases yet. */
/* We don't want to insert any taken items yet. */

INSERT INTO review (itemId, userId, rating, description) VALUES
    (1, 2, 5, "A great toaster."),
    (1, 3, 3, "A decent toaster."),
    (1, 4, 1, "A bad toaster."),
    (2, 2, 5, "A great microwave."),
    (2, 3, 3, "A decent microwave."),
    (2, 4, 1, "A bad microwave."),
    (3, 2, 5, "A great television."),
    (3, 3, 3, "A decent television."),
    (3, 4, 1, "A bad television.");

INSERT INTO featuredItem (itemId) SELECT i.id FROM item i LIMIT 10;

/* We don't want to insert any messages yet. */

