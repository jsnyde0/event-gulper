# event-gulper

Event scraper for Berlin events using LLMs.

## Setup

1. Create a `.env` file in the root directory

## Development with Docker

### Local Development

You can run the entire pipeline stack using Docker Compose:

```bash
cd pipeline
docker compose up --build
```

This starts the orchestrator, database, and scraper services as defined in the `docker-compose.yml` file.

### Debugging

To debug the pipeline using VS Code and Docker:

1. Start the services in debug mode:
   ```bash
   cd pipeline
   docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build
   ```

2. The scraper service will start and wait for the debugger to connect

3. In VS Code, start the "Python: Remote Attach (Docker)" debug configuration


## Testing

Run tests:

```bash
uv run pytest
```

## Project Structure

- `pipeline/`: Event scraping and processing.
- `api/`: API service (WIP).
- `models/`: Shared data models (WIP).

## Contributing

1. Install pre-commit hooks:

```bash
uv run pre-commit install
```
