from pydantic import BaseModel
from datetime import date
from typing import Optional
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

class BookBase(BaseModel):
    id: Optional[int]
    title: str
    author: str
    published_date: date
    summary: str
    genre: str

class BookCreate(BookBase):
    pass

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    published_date: date
    summary: str
    



    class Config:
        orm_mode = True

def create_book(db: Session, book: BookBase):
    db_book = Book(
        title=book.title,
        author=book.author,
        genre=book.genre
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book