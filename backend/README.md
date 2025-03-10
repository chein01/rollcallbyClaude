# Roll Call by AI - Backend

This is the backend service for the Roll Call by AI application, built with FastAPI and MongoDB.

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   ├── endpoints/    # API endpoint modules
│   │   └── dependencies/ # API dependencies
│   ├── core/             # Core functionality
│   │   ├── config.py     # Configuration settings
│   │   ├── security.py   # Security utilities
│   │   └── exceptions.py # Custom exceptions
│   ├── db/               # Database
│   │   ├── models/       # Database models
│   │   └── repositories/ # Database repositories
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── tests/                # Test cases
├── .env                  # Environment variables
├── .env.example         # Example environment variables
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── main.py              # Application entry point
```

## Features

- User authentication and authorization
- Event creation and management
- Daily check-in tracking
- Streak calculation and statistics
- Leaderboard generation
- Achievement and milestone tracking
- Notification system

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB
- Docker (optional)

### Local Development

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:

```bash
uvicorn main:app --reload
```

5. Access the API documentation at http://localhost:8000/docs

### Docker

To run the backend using Docker:

```bash
docker build -t rollcall-backend .
docker run -p 8000:8000 rollcall-backend
```

## API Documentation

The API documentation is automatically generated and available at:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Testing

Run tests with pytest:

```bash
python -m pytest
```