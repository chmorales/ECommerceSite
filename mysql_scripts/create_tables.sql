
/* Move to the database we're using. */
DROP DATABASE CSE305;
CREATE DATABASE CSE305;
USE CSE305;

CREATE TABLE address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    streetNumber INT NOT NULL,
    streetName VARCHAR(20) NOT NULL,
    city VARCHAR(20) NOT NULL,
    zipCode VARCHAR(5) NOT NULL,
    country VARCHAR(10) NOT NULL
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    price FLOAT(10,2) NOT NULL
);

CREATE TABLE person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL,
    email_address VARCHAR(20) UNIQUE NOT NULL,
    cartId INT NOT NULL,
    FOREIGN KEY (cartId) REFERENCES cart(id)
);

CREATE TABLE administrator (
    userId INT NOT NULL,
    FOREIGN KEY (userId) REFERENCES person(id)
);

CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    description VARCHAR(40) NOT NULL
);

CREATE TABLE item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    description VARCHAR(100) NOT NULL,
    price FLOAT(10, 2) NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES person(id),
    FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE purchase (
    buyerId INT NOT NULL,
    cartId INT NOT NULL,
    purchaseDate DATETIME NOT NULL,
    FOREIGN KEY (buyerId) REFERENCES person(id),
    FOREIGN KEY (cartId) REFERENCES cart(id)
);

CREATE TABLE takenItem (
    itemId INT NOT NULL,
    cartId INT NOT NULL,
    FOREIGN KEY (itemId) REFERENCES item(id),
    FOREIGN KEY (cartId) REFERENCES cart(id)
);

CREATE TABLE review (
    itemId INT NOT NULL,
    userId INT NOT NULL,
    rating INT NOT NULL,
    description VARCHAR(40) NOT NULL,
    FOREIGN KEY (itemId) REFERENCES item(id),
    FOREIGN KEY (userId) REFERENCES person(id)
);



