/* Move to the database we're using. */
USE CSE305;

INSERT INTO merchant (first_name, last_name, username, password, email_address) VALUES 
    ('John', 'Doe', 'JDoe', 'password', 'J.Doe@gmail.com'),
    ('Dave', 'Shank', 'DShank', 'password', 'D.Shank@yahoo.com');

INSERT INTO item (name, description, price, seller_id) VALUES 
    ('toothbrush', 'a toothbrush', 34.44, 1),
    ('toothpaste', 'some tasty, tasty toothpaste', 23.21, 1),
    ('catfish', 'two animals in one', 29.99, 2);

