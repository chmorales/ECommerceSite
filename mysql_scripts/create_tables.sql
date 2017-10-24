
/* Move to the database we're using. */
DROP DATABASE CSE305;
CREATE DATABASE CSE305;
USE CSE305;

CREATE TABLE address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    streetNumber INT,
    streetName VARCHAR(20),
    city VARCHAR(20),
    zipCode VARCHAR(5),
    country VARCHAR(10)
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    price FLOAT(10,2)
);

CREATE TABLE person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    password VARCHAR(20),
    email_address VARCHAR(20) UNIQUE,
    cartId INT,
    FOREIGN KEY (cartId) REFERENCES cart(id)
);

CREATE TABLE administrator (
    userId INT,
    FOREIGN KEY (userId) REFERENCES person(id)
);

CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20),
    description VARCHAR(40)
);

CREATE TABLE item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20),
    description VARCHAR(100),
    price FLOAT(10, 2),
    seller_id INT,
    quantity INT,
    category_id INT,
    FOREIGN KEY (seller_id) REFERENCES person(id),
    FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE purchase (
    buyerId INT,
    cartId INT,
    purchaseDate DATETIME,
    FOREIGN KEY (buyerId) REFERENCES person(id),
    FOREIGN KEY (cartId) REFERENCES cart(id)
);

CREATE TABLE takenItem (
    itemId INT,
    cartId INT,
    FOREIGN KEY (itemId) REFERENCES item(id),
    FOREIGN KEY (cartId) REFERENCES cart(id)
);

CREATE TABLE review (
    itemId INT,
    userId INT,
    rating INT,
    description VARCHAR(40),
    FOREIGN KEY (itemId) REFERENCES item(id),
    FOREIGN KEY (userId) REFERENCES person(id)
);
