# Backend - Roommate Expense Splitter

A FastAPI-based backend for the Roommate Expense Splitter application that manages users, groups, and expense splitting logic.

## Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Validation**: Pydantic
- **Authentication**: JWT with Argon2 password hashing
- **Email**: Pydantic email validator

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── models.py            # SQLAlchemy ORM models
│   ├── api/
│   │   ├── main.py          # API router setup
│   │   └── routes/
│   │       ├── users.py     # User endpoints
│   │       └── groups.py    # Group endpoints
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # Authentication & security
│   ├── db/
│   │   └── session.py       # Database session management
│   └── schemas/
│       ├── user.py          # User request/response schemas
│       └── group.py         # Group request/response schemas
├── scripts/
│   ├── run-dev.sh           # Development server startup (Linux/Mac)
│   └── run-dev.ps1          # Development server startup (Windows)
├── sql_scripts/
│   ├── create_tables.sql    # Database schema
│   └── seed_test_data.sql   # Test data
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Models

### User

- `id`: Primary key
- `first_name`: User's first name
- `last_name`: User's last name
- `email`: Unique email address
- `phone`: Optional phone number
- `password_hash`: Hashed password
- `created_at`: Timestamp of creation
- **Relationships**: Group memberships

### Group

- `id`: Primary key
- `name`: Group name
- `created_at`: Timestamp of creation
- **Relationships**: Group memberships

### GroupMembership

- `id`: Primary key
- `user_id`: Foreign key to users
- `group_id`: Foreign key to groups
- `role`: User role in group (owner or member)
- `joined_at`: Timestamp of joining
- **Constraints**: One owner per group, unique membership per user-group pair

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file in the backend directory with the following variables:

```
DATABASE_URL=postgresql://user:password@localhost/roommate_expense_splitter
SECRET_KEY=your-secret-key-here
PROJECT_NAME=Roommate Expense Splitter
API_V1_STR=/api/v1
```

4. Initialize the database:

```bash
psql -U postgres -d roommate_expense_splitter -f sql_scripts/create_tables.sql
psql -U postgres -d roommate_expense_splitter -f sql_scripts/seed_test_data.sql  # Optional
```

## Running the Development Server

### Linux/Mac

```bash
./scripts/run-dev.sh
```

### Windows

```bash
.\scripts\run-dev.ps1
```

Or directly with uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Users

- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Groups

- `POST /api/v1/groups/` - Create a new group
- `GET /api/v1/groups/{group_id}` - Get group details
- `PUT /api/v1/groups/{group_id}` - Update group
- `DELETE /api/v1/groups/{group_id}` - Delete group

See the Swagger UI for complete endpoint documentation and request/response schemas.

## Development Notes

- The application uses SQLAlchemy ORM with PostgreSQL
- Authentication is handled using JWT tokens with Argon2 password hashing
- Pydantic schemas are used for request validation and response serialization
- Database sessions are managed per request
- The API uses tags for automatic OpenAPI documentation organization

## Testing

To run tests (don't exist yet):

```bash
pytest
```
