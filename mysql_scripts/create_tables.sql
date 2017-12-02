
/* Move to the database we're using. */
DROP DATABASE IF EXISTS CSE305;
CREATE DATABASE CSE305;
USE CSE305;

CREATE TABLE address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    streetNumber INT NOT NULL,
    streetName TEXT NOT NULL,
    city TEXT NOT NULL,
    zipCode VARCHAR(10) NOT NULL,
    country TEXT NOT NULL,
    CHECK (CHAR_LENGTH(zipCode) >= 5),
    CHECK (streetNumber > 0)
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    price FLOAT(10,2) NOT NULL,
    CHECK (price > 0) -- Cannot have a negative price.
);

CREATE TABLE person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password VARCHAR(50) NOT NULL,
    email_address VARCHAR(100) UNIQUE NOT NULL,
    cartId INT NOT NULL,
    FOREIGN KEY (cartId) REFERENCES cart(id),
    CHECK (first_name <> ''),
    CHECK (last_name <> ''),
    CHECK (password <> '' and CHAR_LENGTH(password) > 5)
);

CREATE TABLE administrator (
    userId INT NOT NULL,
    FOREIGN KEY (userId) REFERENCES person(id)
);

CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    CHECK (name <> ''),
    CHECK (description <> '')
);

CREATE TABLE item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price FLOAT(10, 2) NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    category_id INT NOT NULL,
    listed BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (seller_id) REFERENCES person(id),
    FOREIGN KEY (category_id) REFERENCES category(id),
    CHECK (name <> ''),
    CHECK (price > 0),
    CHECK (quantity >= 0)
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
    quantity INT NOT NULL,
    FOREIGN KEY (itemId) REFERENCES item(id),
    FOREIGN KEY (cartId) REFERENCES cart(id)
);

CREATE TABLE review (
    itemId INT NOT NULL,
    userId INT NOT NULL,
    rating INT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (itemId) REFERENCES item(id),
    FOREIGN KEY (userId) REFERENCES person(id),
    CHECK (rating >= 1 and rating <= 5),
    CHECK (description <> '')
);

CREATE TABLE featuredItem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    itemId INT NOT NULL,
    FOREIGN KEY (itemId) REFERENCES item(id)
);
