USE CSE305;

INSERT INTO address (streetNumber, streetName, city, zipCode, country) VALUES
    (5, "Somerset Drive", "Holbrook", "11741", "USA");

INSERT INTO cart (price) VALUES
    (0.0);

INSERT INTO person (first_name, last_name, password, email_address, cartId) VALUES
    ("Bob", "Admin", "pa", "B.Admin@gmail.com", 1);

INSERT INTO administrator (userId) VALUES
    (1);

INSERT INTO category (name, description) VALUES
    ("Electronics", "Electric Things");

INSERT INTO item (name, description, price, seller_id, quantity, category_id) VALUES
    ("TV", "a TV", 56.66, 1, 2, 1);

/* We don't want to insert any purchases yet. */
/* We don't want to insert any taken items yet. */

INSERT INTO review (itemId, userId, rating, description) VALUES
    (1, 1, 5, "A great tv wow.");
