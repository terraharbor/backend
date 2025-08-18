CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    disabled BOOLEAN NOT NULL DEFAULT FALSE,
    sha512_hash VARCHAR(128) NOT NULL,
    token VARCHAR(128),
    token_validity INTEGER
);