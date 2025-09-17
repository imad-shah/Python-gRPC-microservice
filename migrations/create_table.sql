create table `books`.`books` (
    isbn_number bigint,
    title varchar(255),
    author varchar(255),
    copies_remaining int,
    total_copies int,
    primary key (isbn),
);
