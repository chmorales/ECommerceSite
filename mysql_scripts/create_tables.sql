
/* Move to the database we're using. */
USE CSE305;

/* Drop the tables if they already exist, in essence restarting the database. */
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS merchant;

CREATE TABLE person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    username VARCHAR(20) UNIQUE,
    password VARCHAR(20),
    email_address VARCHAR(20) UNIQUE
);

CREATE TABLE item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20),
    description VARCHAR(100),
    /* What do we want to do for prices?
    Right now, the max price is $99,999,999.99 */
    price FLOAT(10, 2),
    seller_id INT,
    quantity INT,
    FOREIGN KEY (seller_id) REFERENCES person(id)
);
