# Tintas AI Loomi - Backend API

Backend API for paint system with AI, built with FastAPI.

## Technologies

- **FastAPI** - Modern web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - Python ORM
- **Alembic** - Database migrations
- **Structlog** - Structured logging
- **Docker** - Containerization

## Installation

### Local Development

```bash
cd api
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp env.example .env
# Configure .env file
alembic upgrade head
python main.py
```

### Docker

```bash
cd api
docker-compose up -d
```

## Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Health Checks

- `GET /health/` - Basic health check

## Project Structure

```text
api/
├── app/
│   ├── core/           # Configuration and logs
│   ├── infrastructure/ # Database and middleware
│   └── presentation/   # API routes
├── alembic/           # Migrations
├── main.py           # Entry point
└── requirements.txt  # Dependencies
```

## Configuration

All settings via environment variables. See `env.example`.
