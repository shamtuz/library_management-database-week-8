Library Management System Database Documentation
Overview
The Library Management System database is designed to manage a library's operations, including tracking books, members, staff, and borrowing records. It is implemented in MySQL and consists of four tables: Books, Members, Staff, and Borrowing. The database supports a web-based CRUD API (built with FastAPI) for managing books and borrowing records, ensuring data integrity through constraints and relationships.
Database Schema
The following SQL code creates the database schema with all tables, constraints, and relationships.
-- Library Management System Database
-- File: library_management.sql

-- Create Books table
CREATE TABLE Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    publication_year INT,
    available_copies INT NOT NULL DEFAULT 1,
    CHECK (available_copies >= 0)
);

-- Create Members table
CREATE TABLE Members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    join_date DATE NOT NULL
);

-- Create Staff table
CREATE TABLE Staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hire_date DATE NOT NULL,
    role ENUM('Librarian', 'Assistant', 'Manager') NOT NULL
);

-- Create Borrowing table (junction table for Books, Members, and Staff)
CREATE TABLE Borrowing (
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    staff_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE RESTRICT
);

Entity-Relationship Diagram (ERD)
The ERD visualizes the tables, their attributes, and relationships. It is written in Mermaid syntax and can be rendered in tools like Mermaid Live Editor or GitHub Markdown.
erDiagram
    Books {
        INT book_id PK
        VARCHAR title
        VARCHAR author
        VARCHAR isbn UK
        INT publication_year
        INT available_copies
    }

    Members {
        INT member_id PK
        VARCHAR first_name
        VARCHAR last_name
        VARCHAR email UK
        VARCHAR phone
        DATE join_date
    }

    Staff {
        INT staff_id PK
        VARCHAR first_name
        VARCHAR last_name
        VARCHAR email UK
        DATE hire_date
        ENUM role
    }

    Borrowing {
        INT borrow_id PK
        INT book_id FK
        INT member_id FK
        INT staff_id FK
        DATE borrow_date
        DATE return_date
    }

    Books ||--o{ Borrowing : "has"
    Members ||--o{ Borrowing : "has"
    Staff ||--o{ Borrowing : "processes"

Table Descriptions
1. Books
Stores information about books in the library.



Column
Type
Constraints
Description



book_id
INT
PRIMARY KEY, AUTO_INCREMENT
Unique identifier for each book.


title
VARCHAR(255)
NOT NULL
Title of the book.


author
VARCHAR(100)
NOT NULL
Author of the book.


isbn
VARCHAR(13)
UNIQUE, NOT NULL
Unique ISBN (13-digit).


publication_year
INT

Year the book was published (optional).


available_copies
INT
NOT NULL, DEFAULT 1, CHECK (>=0)
Number of copies available for borrowing.


2. Members
Stores information about library members.



Column
Type
Constraints
Description



member_id
INT
PRIMARY KEY, AUTO_INCREMENT
Unique identifier for each member.


first_name
VARCHAR(50)
NOT NULL
Member's first name.


last_name
VARCHAR(50)
NOT NULL
Member's last name.


email
VARCHAR(100)
UNIQUE, NOT NULL
Member's unique email address.


phone
VARCHAR(15)

Member's phone number (optional).


join_date
DATE
NOT NULL
Date the member joined the library.


3. Staff
Stores information about library staff.



Column
Type
Constraints
Description



staff_id
INT
PRIMARY KEY, AUTO_INCREMENT
Unique identifier for each staff member.


first_name
VARCHAR(50)
NOT NULL
Staff's first name.


last_name
VARCHAR(50)
NOT NULL
Staff's last name.


email
VARCHAR(100)
UNIQUE, NOT NULL
Staff's unique email address.


hire_date
DATE
NOT NULL
Date the staff was hired.


role
ENUM
NOT NULL
Role: Librarian, Assistant, or Manager.


4. Borrowing
Tracks borrowing transactions, linking books, members, and staff.



Column
Type
Constraints
Description



borrow_id
INT
PRIMARY KEY, AUTO_INCREMENT
Unique identifier for each borrowing record.


book_id
INT
NOT NULL, FOREIGN KEY
References book_id in Books.


member_id
INT
NOT NULL, FOREIGN KEY
References member_id in Members.


staff_id
INT
NOT NULL, FOREIGN KEY
References staff_id in Staff.


borrow_date
DATE
NOT NULL
Date the book was borrowed.


return_date
DATE

Date the book was returned (optional).


Relationships

Books to Borrowing: One-to-Many (||--o{).
One book can be borrowed multiple times.
Foreign Key: Borrowing.book_id references Books.book_id (ON DELETE CASCADE).


Members to Borrowing: One-to-Many (||--o{).
One member can borrow multiple books.
Foreign Key: Borrowing.member_id references Members.member_id (ON DELETE CASCADE).


Staff to Borrowing: One-to-Many (||--o{).
One staff member can process multiple borrowing transactions.
Foreign Key: Borrowing.staff_id references Staff.staff_id (ON DELETE RESTRICT).


Books and Members: Many-to-Many (via Borrowing).
A book can be borrowed by multiple members over time, and a member can borrow multiple books.
The Borrowing table acts as a junction table.



Constraints

Primary Keys: book_id, member_id, staff_id, borrow_id (auto-incremented).
Foreign Keys:
Borrowing.book_id → Books.book_id (CASCADE on delete).
Borrowing.member_id → Members.member_id (CASCADE on delete).
Borrowing.staff_id → Staff.staff_id (RESTRICT on delete).


Unique Keys: isbn (Books), email (Members, Staff).
Not Null: Ensures required fields (e.g., title, author, borrow_date) are always provided.
Check: available_copies ≥ 0 in Books.
Enum: role in Staff restricted to 'Librarian', 'Assistant', 'Manager'.

Assumptions

The database is hosted on a MySQL server running on localhost with a database named library.
The associated FastAPI application handles CRUD operations for Books and Borrowing, validating foreign keys (book_id, member_id, staff_id) before insertions or updates.
Test data (e.g., members, staff) must be inserted manually into Members and Staff tables to test Borrowing operations.
The isbn is assumed to be a 13-digit string (modern ISBN-13 format).
The role ENUM in Staff is fixed to three values; additional roles require schema modification.

Usage Notes

Setup:
Create the database: CREATE DATABASE library;.
Apply the schema: mysql -u your_username -p library < library_management.sql.
Replace your_username and provide your MySQL password.


Integration:
The database integrates with a FastAPI application (using mysql-connector-python) for CRUD operations.
Ensure the API validates foreign keys to prevent invalid Borrowing records.


Testing:
Insert test data into Books, Members, and Staff before testing Borrowing.
Example:INSERT INTO Members (first_name, last_name, email, phone, join_date)
VALUES ('John', 'Doe', 'john.doe@example.com', '1234567890', '2025-01-01');

INSERT INTO Staff (first_name, last_name, email, hire_date, role)
VALUES ('Jane', 'Smith', 'jane.smith@example.com', '2024-01-01', 'Librarian');

INSERT INTO Books (title, author, isbn, publication_year, available_copies)
VALUES ('1984', 'George Orwell', '1234567890123', 1949, 5);




Rendering the ERD:
Copy the Mermaid code into Mermaid Live Editor or a Mermaid-compatible Markdown renderer (e.g., GitHub).
The diagram will display tables, attributes, and relationships.



This documentation provides a complete reference for the Library Management System database, suitable for developers, database administrators, or stakeholders.
