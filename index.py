from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import Book as BookModel
from schemas import BookCreate, Book as BookSchema
from database import get_db_connection
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Import your Base model

# Constants
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database URL (update with your actual database URL)
DATABASE_URL = "sqlite:///./books.db"  # Example for SQLite

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI instance
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Yield the session to the caller
    finally:
        db.close()  # Close the session when done

# JWT Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CRUD Operations
@app.post("/books/", response_model=BookSchema)  # Ensure response_model is set correctly
def create_book(book: BookSchema, db: Session = Depends(get_db)):
    # Create an instance of the SQLAlchemy model
    db_book = BookModel(  # Use the SQLAlchemy model here
        title=book.title,
        author=book.author,
        genre=book.genre,
        summary=book.summary,
        published_date=book.published_date
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=list[BookSchema])
def read_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    books = db.query(BookModel).offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=BookSchema)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=BookSchema)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    return db_book

@app.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted"}

# Real-Time Updates (SSE)
@app.get("/events/")
async def event_stream():
    async def event_generator():
        while True:
            yield f"data: {datetime.now()}\n\n"
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())

# Create the database tables
def create_database():
    Base.metadata.create_all(bind=engine)

# Call the function to create tables
create_database()