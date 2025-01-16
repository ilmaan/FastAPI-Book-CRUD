# Organized imports
from fastapi import FastAPI, Depends, HTTPException, status, Security, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Book as BookModel, Base  # Import your Base model
from schemas import BookCreate, Book as BookSchema
from database import get_db_connection
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext  # For password hashing
import asyncio
from pydantic import BaseModel


from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates




# Constants for authentication
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "sqlite:///./books.db"  # Database URL



# Create the SQLAlchemy engine and session 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Creating FastAPI instance
app = FastAPI(docs_url="/swagger", redoc_url="/redoc")





# @app.get("/")
# async def read_root():
#     return {"message": "BOOKS CRUD FASTAPI","FOR TESTING PURPOSES ONLY":'FOR AUTHENTICSTION USE',"username":'testuser',"password":"password"}



# Specify the directory where your templates are stored
templates = Jinja2Templates(directory=".")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWT Authentication setup for authentication

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model for demonstration purposes

# ADDED User class for authentication ----- tetsing username = testuser  testing password = password
class User:
    def __init__(self, username: str, full_name: str, email: str, hashed_password: str):
        self.username = username
        self.full_name = full_name
        self.email = email
        self.hashed_password = hashed_password

# test user database
test_user = {
    "testuser": User(
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        hashed_password=pwd_context.hash("password")
    )
}



# Function to verify password - ref fastapi documentation
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Function to create JWT tokene
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# Login endpoint for authentication Note --- API cannot be hit withiout authentication
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = test_user.get(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# WebSocket clients list for real time display for books records and db changes
connected_clients = []





# CRUD Operations APIs for Books 


# To Create book
@app.post("/books/", response_model=BookSchema, tags=["Books"])
async def create_book(book: BookSchema, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_book = BookModel(
        title=book.title,
        author=book.author,
        genre=book.genre.value,
        published_date=book.published_date,
        summary=book.summary
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    await notify_clients(f"New book created: {db_book.title} by {db_book.author}")
    return db_book





# To Get books PPagination is added
@app.get("/books/", response_model=list[BookSchema], tags=["Books"])
async def read_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return db.query(BookModel).offset(skip).limit(limit).all()


# To get specific book
@app.get("/books/{book_id}", response_model=BookSchema, tags=["Books"])
async def read_book(book_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await notify_clients(f"Book details: {book.title} by {book.author}")
    return book


# To Update book details
@app.put("/books/{book_id}", response_model=BookSchema, tags=["Books"])
async def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    await notify_clients(f"Book updated: {db_book.title} by {db_book.author}")
    return db_book


# To Delete book from db
@app.delete("/books/{book_id}", response_model=dict, tags=["Books"])
async def delete_book(book_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await notify_clients(f"Book deleted: {db_book.title} by {db_book.author}")
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted"}

# Notify all connected WebSocket clients
async def notify_clients(message: str):
    for client in connected_clients:
        await client.send_text(message)




# Using websockets to disply real time changes on server events
# Used HTML inside function for now so everything is at same place for easy modification
@app.get("/booksdisplay", tags=["BOOKS REAL TIME UPDATES"])
async def get_books_display(db: Session = Depends(get_db)):
    books = db.query(BookModel).all()
    books_list = "".join(
        f"<tr><td>{book.id}</td><td>{book.title}</td><td>{book.author}</td><td>{book.genre}</td><td>{book.summary}</td><td>{book.published_date}</td></tr>"
        for book in books
    )
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Real Time Books Display -- Using Websockets</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:hover {{ background-color: #f1f1f1; }}
                #messages {{ list-style-type: none; padding: 0; }}
                #messages li {{ background: #e2e2e2; margin: 5px 0; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>WebSocket BOOK REAL TIME DISPLAYS </h1>
            <ul id='messages'></ul>
            <h1>All Books</h1>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Author</th>
                        <th>Genre</th>
                        <th>Summary</th>
                        <th>Published Date</th>
                    </tr>
                </thead>
                <tbody>
                    {books_list}
                </tbody>
            </table>
            <script>
                var ws = new WebSocket('wss://fastapi-book-crud-nvz8.onrender.com//ws');
                ws.onopen = function() {{ console.log('WebSocket connection established'); }};
                ws.onmessage = function(event) {{
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    var content = document.createTextNode(event.data);
                    message.appendChild(content);
                    messages.appendChild(message);
                }};
                function sendMessage(event) {{
                    var input = document.getElementById('messageText');
                    ws.send(input.value);
                    input.value = '';
                    event.preventDefault();
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

# WebSocket endpoint

# Websocket endpoint for message displays
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    await websocket.send_text("ALL UPDATES WILL BE DISPLAYED HERE !!!!!")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(websocket)  # Remove the client from the list on disconnect