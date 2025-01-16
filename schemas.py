from pydantic import BaseModel
from datetime import date
from typing import Optional, Annotated
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from enum import Enum
from pydantic import constr

Base = declarative_base()

class BookBase(BaseModel):
    # id: Optional[int]
    title: Annotated[str, constr(min_length=1, max_length=100)]
    author: Annotated[str, constr(min_length=1, max_length=50)]
    published_date: date
    summary: str
    genre: str

class BookCreate(BookBase):
    pass



class Genres(Enum):
    Adventure="Adventure"
    Action="Action"
    Comdedy="Comdedy"
    string="string"



class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: Genres
    published_date: date
    summary: str
    



    class Config:
        orm_mode = True

def create_book(db: Session, book: BookBase):
    db_book = Book(
        title=book.title,
        author=book.author,
        genre=book.genre,
        published_date=book.published_date,
        summary=book.summary
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


