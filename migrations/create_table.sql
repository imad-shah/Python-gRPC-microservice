create table `books`.`books` (
    id char(36),
    title varchar(255),
    author varchar(255),
    description varchar(4095),
    checked_out bool,
    isbn_number bigint,
    primary key (id),
    unique (isbn_number)
);