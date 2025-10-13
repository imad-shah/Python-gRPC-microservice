CREATE TABLE IF NOT EXISTS Books (
    isbn VARCHAR(255),
    title VARCHAR(255),
    author VARCHAR(255),
    copies_remaining INT,
    total_copies INT,
    PRIMARY KEY (isbn)
);
