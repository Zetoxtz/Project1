CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year VARCHAR NOT NULL
);

CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

"INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {
    "isbn": isbn, "title": title, "author": author, "year": year

"INSERT INTO users (name, username, email, password) VALUES
    (:name, :username, :email, :password)", {
    "name": name, "username": username, "email": email, "password": password
    }
