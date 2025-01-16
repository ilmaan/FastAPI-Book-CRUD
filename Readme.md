# FastAPI Book Management Application

This is a FastAPI application for managing a collection of books. It provides a RESTful API for CRUD operations on books and includes JWT-based authentication. Additionally, it supports real-time updates using WebSockets.

## Features

- **CRUD Operations**: Create, read, update, and delete books.
- **Authentication**: Secure endpoints using JWT tokens.
- **Real-Time Updates**: Display real-time updates of book records using WebSockets.
- **Swagger UI**: Interactive API documentation available at `/swagger`.
- **ReDoc**: Alternative API documentation available at `/redoc`.

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **SQLite**: Database for storing book records.
- **JWT**: JSON Web Tokens for authentication.
- **WebSockets**: For real-time communication.

## Setup Instructions

### Prerequisites

- Python 3.7+
- Virtual environment (optional but recommended)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment** (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   uvicorn index:app --reload
   ```

   The application will be available at `http://localhost:8000`.

## Usage

### Authentication

- Obtain a JWT token by sending a POST request to `/token` with a valid username and password.
- Use the token to authenticate requests to protected endpoints.

### API Endpoints

- **POST /books/**: Create a new book.
- **GET /books/**: Retrieve a list of books with pagination.
- **GET /books/{book_id}**: Retrieve details of a specific book.
- **PUT /books/{book_id}**: Update details of a specific book.
- **DELETE /books/{book_id}**: Delete a specific book.

### Real-Time Updates

- Access real-time book updates at `/booksdisplay`.
- WebSocket endpoint available at `/ws` for receiving real-time messages.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For questions or support, please contact [your-email@example.com].
