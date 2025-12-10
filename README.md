# Formbricks Automation

A Python CLI tool to run, manage, and seed a local Formbricks instance with realistic data using LLM-generated content.

## Features

- **Docker-based setup**: One command to start/stop Formbricks locally
- **LLM-powered data generation**: Uses OpenAI to generate realistic surveys, users, and responses
- **API-only seeding**: All data is seeded via Formbricks Management and Client APIs

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- OpenAI API key (for data generation)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Singh-akshay03/formbricks-automation.git
   cd formbricks-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template and configure:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

## Usage

### 1. Start Formbricks

```bash
python main.py formbricks up
```

This starts PostgreSQL, Redis, and Formbricks containers. Wait for the health check to pass, then access Formbricks at http://localhost:3000.

**First-time setup:**
1. Create an account at http://localhost:3000
2. Go to Settings > API Keys and generate an API key
3. Note your Organization ID and Environment ID from the URL
4. Update `.env` with these values

### 2. Generate Data

```bash
python main.py formbricks generate
```

Generates realistic data using OpenAI:
- 5 unique surveys with varied question types
- 10 users with Manager/Owner roles
- Saves to `data/generated_data.json`

### 3. Seed Formbricks

```bash
python main.py formbricks seed
```

Seeds the generated data into Formbricks via APIs:
- Creates users via Management API
- Creates surveys via Management API
- Generates and submits responses via Client API

### 4. Stop Formbricks

```bash
python main.py formbricks down
```

Stops all Docker containers. Data is preserved in Docker volumes.

To remove all data:
```bash
docker-compose down -v
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for data generation | For `generate` |
| `FORMBRICKS_API_KEY` | Formbricks API key | For `seed` |
| `ORGANIZATION_ID` | Formbricks organization ID | For `seed` |
| `ENVIRONMENT_ID` | Formbricks environment ID | For `seed` |
| `FORMBRICKS_URL` | Formbricks URL (default: http://localhost:3000) | Optional |
| `OPENAI_MODEL` | OpenAI model (default: gpt-4o-mini) | Optional |

## Project Structure

```
formbricks-automation/
├── main.py                 # CLI entry point
├── docker-compose.yml      # Docker services configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── api/
│   └── client.py           # Formbricks API client
├── commands/
│   ├── up.py               # Start command
│   ├── down.py             # Stop command
│   ├── generate.py         # Generate command
│   └── seed.py             # Seed command
├── generators/
│   └── data_generator.py   # LLM data generator
├── utils/
│   ├── config.py           # Configuration management
│   └── logger.py           # Logging utilities
└── data/
    └── generated_data.json # Generated data (after running generate)
```

## Seeding Details

The seed command creates:
- **5 surveys** with diverse types (Customer Satisfaction, NPS, Product Feedback, etc.)
- **10 users** with Manager and Owner roles
- **1+ response per survey** with realistic, contextual answers

All seeding is done via Formbricks APIs only (no direct database manipulation).

## License

MIT
