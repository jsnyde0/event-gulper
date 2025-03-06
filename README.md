# event-gulper

Event scraper for Berlin events using Agentic AI.

## Setup

1. Create a `.env` file in the root directory

2. Install dependencies:

```bash
uv sync --all-extras --dev
```

## Development

1. Start the Prefect development server:

```bash
uv run prefect server start
```

The Prefect UI will be available at [http://127.0.0.1:4200](http://127.0.0.1:4200).

2. Register your scraper deployment by running:

```bash
uv run -m core.serve_scraper
```

This command uses the `serve()` method (in `serve_scraper.py`) to register the deployment named `siegessaeule-scraper-deployment` without an automatic interval. The flow will only run when you trigger it manually from the Prefect dashboard (or via an API call).

3. Run tests:

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

2. Format and lint code:

```bash
uv run ruff check .
uv run ruff format .
```
