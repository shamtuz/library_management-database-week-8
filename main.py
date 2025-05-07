from fastapi import FastAPI, Depends, HTTPException
from mysql.connector import Error, IntegrityError
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from contextlib import contextmanager
import mysql.connector

# Database Connection
@contextmanager
def get_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="your_username",  # Replace with your MySQL username
        password="your_password",  # Replace with your MySQL password
        database="library"
    )
    try:
        yield conn
    finally:
        conn.close()

# Pydantic Models
class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=13, max_length=13)
    publication_year: Optional[int] = None
    available_copies: int = Field(..., ge=0)

class Borrowing(BaseModel):
    book_id: int = Field(..., gt=0)
    member_id: int = Field(..., gt=0)
    staff_id: int = Field(..., gt=0)
    borrow_date: date
    return_date: Optional[date] = None

# FastAPI Application
app = FastAPI(title="Library Management API")

# Helper function to check if a record exists
def check_exists(db, table: str, column: str, value: int) -> bool:
    cursor = db.cursor()
    query = f"SELECT 1 FROM {table} WHERE {column} = %s"
    cursor.execute(query, (value,))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists

# CRUD for Books
@app.post("/books/", response_model=Book)
def create_book(book: Book, db=Depends(get_db)):
    cursor = db.cursor()
    query = """
    INSERT INTO Books (title, author, isbn, publication_year, available_copies)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (book.title, book.author, book.isbn, book.publication_year, book.available_copies)
    try:
        cursor.execute(query, values)
        db.commit()
        return book
    except IntegrityError as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="ISBN already exists")
        raise HTTPException(status_code=400, detail=str(e))
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@app.get("/books/", response_model=List[Book])
def read_books(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT title, author, isbn, publication_year, available_copies FROM Books")
        books = cursor.fetchall()
        return books
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: Book, db=Depends(get_db)):
    cursor = db.cursor()
    query = """
    UPDATE Books
    SET title=%s, author=%s, isbn=%s, publication_year=%s, available_copies=%s
    WHERE book_id=%s
    """
    values = (book.title, book.author, book.isbn, book.publication_year, book.available_copies, book_id)
    try:
        cursor.execute(query, values)
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
    except IntegrityError as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="ISBN already exists")
        raise HTTPException(status_code=400, detail=str(e))
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Books WHERE book_id=%s", (book_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        return {"detail": "Book deleted"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

# CRUD for Borrowing
@app.post("/borrowing/", response_model=Borrowing)
def create_borrowing(borrowing: Borrowing, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        # Validate foreign keys
        if not check_exists(db, "Books", "book_id", borrowing.book_id):
            raise HTTPException(status_code=400, detail="Book does not exist")
        if not check_exists(db, "Members", "member_id", borrowing.member_id):
            raise HTTPException(status_code=400, detail="Member does not exist")
        if not check_exists(db, "Staff", "staff_id", borrowing.staff_id):
            raise HTTPException(status_code=400, detail="Staff does not exist")

        query = """
        INSERT INTO Borrowing (book_id, member_id, staff_id, borrow_date, return_date)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            borrowing.book_id,
            borrowing.member_id,
            borrowing.staff_id,
            borrowing.borrow_date,
            borrowing.return_date
        )
        cursor.execute(query, values)
        db.commit()
        return borrowing
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@app.get("/borrowing/", response_model=List[Borrowing])
def read_borrowing(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT book_id, member_id, staff_id, borrow_date, return_date FROM Borrowing")
        borrowings = cursor.fetchall()
        return borrowings
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@app.put("/borrowing/{borrow_id}", response_model=Borrowing)
def update_borrowing(borrow_id: int, borrowing: Borrowing, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        # Validate foreign keys
        if not check_exists(db, "Books", "book_id", borrowing.book_id):
            raise HTTPException(status_code=400, detail="Book does not exist")
        if not check_exists(db, "Members", "member_id", borrowing.member_id):
            raise HTTPException(status_code=400, detail="Member does not exist")
        if not check_exists(db, "Staff", "staff_id", borrowing.staff_id):
            raise HTTPException(status_code=400, detail="Staff does not exist")

        query = """
        UPDATE Borrowing
        SET book_id=%s, member_id=%s, staff_id=%s, borrow_date=%s, return_date=%s
        WHERE borrow_id=%s
        """
        values = (
            borrowing.book_id,
            borrowing.member_id,
            borrowing.staff_id,
            borrowing.borrow_date,
            borrowing.return_date,
            borrow_id
        )
        cursor.execute(query, values)
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Borrowing record not found")
        return borrowing
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@app.delete("/borrowing/{borrow_id}")
def delete_borrowing(borrow_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Borrowing WHERE borrow_id=%s", (borrow_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Borrowing record not found")
        return {"detail": "Borrowing record deleted"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
