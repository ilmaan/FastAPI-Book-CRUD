from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from schemas import Book

DATABASE_URL = "sqlite:///./books.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    published_date = Column(Date)
    summary = Column(String)
    genre = Column(String)

    def create_book(self, book: 'Book') -> None:
        if len(book.author) <= 5:
            raise ValueError("Author name must be greater than 5 characters.")
        self.validate_title(book.title)
        self.validate_published_date(book.published_date)
        self.validate_summary(book.summary)
        self.validate_genre(book.genre)

    def validate_title(self, title: str) -> None:
        if not title or len(title) < 3:
            raise ValueError("Title must be at least 3 characters long.")

    def validate_published_date(self, published_date: Date) -> None:
        if published_date is None:
            raise ValueError("Published date is required.")

    def validate_summary(self, summary: str) -> None:
        if not summary or len(summary) < 10:
            raise ValueError("Summary must be at least 10 characters long.")

    def validate_genre(self, genre: str) -> None:
        if not genre:
            raise ValueError("Genre is required.")


    def create_book(self, book: Book):
        if len(book.author) <= 5:
            raise ValueError("Author name must be greater than 5 characters.")
        
