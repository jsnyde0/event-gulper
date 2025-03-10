# Event Gulper Pipeline

Event scraping pipeline component using LLMs.

## Overview

This package contains the event scraping and processing pipeline that:
1. Scrapes events from various sources (currently Siegessäule)
2. Uses LLMs to extract structured data
3. Stores events in PostgreSQL database

## Development

See the root README.md for complete development instructions.

### Pipeline-Specific Configuration

The pipeline can be configured using environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `PREFECT_API_URL`: Prefect server API URL
- (Add other pipeline-specific variables)

### Module Structure

- `core/`: Core pipeline components and utilities
- `orchestration/`: Prefect flows and deployments
- `tests/`: Pipeline-specific tests

## Testing

Run pipeline-specific tests:
```bash
cd pipeline
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
