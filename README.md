# KIU - Flight Journey Finder

API service that finds possible flight journeys between cities, considering connections and time constraints.

## Features

- Find direct and connecting flights between cities
- Validate connection times
- Cache flight data
- Configurable constraints (max flight time, connection times, etc.)

## Requirements

- Docker
- Docker Compose
- Python 3.12 (for local development)

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a `.env` file based on the example:
```bash
cp .env.example .env
```

3. Build and run the service:
```bash
docker compose build
docker compose up
```

The API will be available at `http://localhost:8000`

## API Documentation

With the server running, you can access:
- Swagger UI at `http://localhost:8000/docs`
- ReDoc at `http://localhost:8000/redoc`

## API Endpoints

### Search Journeys

```
GET /journeys/search?from={origin}&to={destination}&departure_date={YYYY-MM-DD}
```

Example:
```bash
curl "http://localhost:8000/journeys/search?from=MAD&to=BUE&departure_date=2024-03-20"
```

## Configuration

The following environment variables can be configured in `.env`:

- `FLIGHT_EVENTS_URL`: URL of the flight events API
- `MIN_WAIT_TIME_HOURS`: Minimum connection time (default: 1)
- `MAX_WAIT_TIME_HOURS`: Maximum connection time (default: 4)
- `MAX_FLIGHT_DURATION_HOURS`: Maximum total journey time (default: 24)
- `MAX_FLIGHT_EVENTS`: Maximum number of flights in a journey (default: 2)
- `CACHE_TTL_SECONDS`: Cache time-to-live in seconds (default: 600)

## Development

### Running Tests

Unit tests:
```bash
pytest tests/unit/
```

Integration tests:
```bash
pytest tests/integration/
```

### Code Quality

The project uses:
- mypy for type checking
- flake8 for linting
- pytest for testing

Run all checks:
```bash
mypy --explicit-package-bases app
flake8 app tests --exclude=__init__.py
pytest tests/
```

## CI/CD

GitHub Actions workflows run:
- Type checking (mypy)
- Linting (flake8)
- Unit tests
- Integration tests

## License

MIT