# event-gulper

Event scraper for Berlin events using Agentic AI.

## Project Structure

- `pipeline/`: Event scraping and processing pipeline
- `models/`: Shared data models
- `api/`: API service

## Setup

Create a `.env` file in the root directory (see `.env.example`)


## Development

### Using Docker (Recommended)

1. Start all services:
```bash
docker compose up --build
```

This starts:
- PostgreSQL database
- Prefect orchestrator (UI at http://localhost:4200)
- Pipeline service

### Debugging with Docker

1. Start services in debug mode:
```bash
docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build
```

2. The pipeline service will wait for debugger connection on port 5678

3. Use VS Code's "Python: Remote Attach" to connect to the debugger

### Run tests

```bash
uv run pytest
```


## Contributing

1. Install pre-commit hooks:

```bash
uv run pre-commit install
```

2. Format and lint code:

```bash
uv run ruff check .
uv run ruff format .
```
