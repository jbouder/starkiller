# Starkiller

An experimental Generative BI (Business Intelligence) tool that leverages Large Language Models to generate data visualizations on the fly.

## Overview

Starkiller reimagines traditional BI dashboarding by using AI to dynamically create data visualizations based on natural language queries. Instead of pre-built dashboards, users can ask questions about their data and receive intelligent, contextual visualizations generated in real-time.

## Features

- **AI-Powered Visualization**: Generate charts, graphs, and dashboards using natural language
- **Dynamic Analysis**: Ask questions and get instant visual insights
- **Flexible Data Sources**: Connect to various data sources and databases
- **Interactive Dashboards**: Explore and refine visualizations interactively
- **Smart Recommendations**: AI suggests relevant visualizations based on your data

## Tech Stack

| Frontend              | Backend              |
| --------------------- | -------------------- |
| React 19 + TypeScript | Python FastAPI       |
| Vite                  | SQLAlchemy (async)   |
| Tailwind CSS          | Anthropic Claude     |
| shadcn/ui             | Pandas/NumPy         |
| Recharts              | Alembic + PostgreSQL |

## Quick Start (Docker Compose)

The easiest way to run Starkiller is with Docker Compose, which starts the UI, API, and PostgreSQL database together.

### Prerequisites

- Docker and Docker Compose
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/starkiller.git
cd starkiller

# Configure the API environment
cp api/.env.example api/.env
```

Edit `api/.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Start the Stack

```bash
docker compose up --build
```

### 3. Initialize the Database

In a new terminal, run migrations and seed sample data:

```bash
# Run database migrations
docker compose exec api alembic upgrade head

# Seed external sample databases
docker compose exec api python scripts/seed_connection_data.py

# Seed application data sources
docker compose exec api python scripts/seed_data_sources.py

# Seed sample dashboards
docker compose exec api python scripts/seed_dashboards.py
```

### 4. Access the Application

| Service            | URL                         |
| ------------------ | --------------------------- |
| UI                 | http://localhost:3000       |
| API                | http://localhost:8000       |
| API Docs (Swagger) | http://localhost:8000/docs  |
| API Docs (ReDoc)   | http://localhost:8000/redoc |

---

## Local Development (Without Docker)

For development without Docker, you'll need to run the frontend and backend separately.

### Prerequisites

- Node.js 18+ and npm 9+
- Python 3.11+
- PostgreSQL 15+
- An [Anthropic API key](https://console.anthropic.com/)

### Backend Setup

```bash
cd api

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run migrations
alembic upgrade head

# Start the API server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd ui

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Seed Sample Data (Local)

With PostgreSQL running locally:

```bash
cd api
source .venv/bin/activate

# Set admin connection for creating external databases
export ADMIN_DB_URL=postgresql://postgres:postgres@localhost:5432/postgres

# Seed in order
python scripts/seed_connection_data.py  # External sample databases
python scripts/seed_data_sources.py     # Application data sources
python scripts/seed_dashboards.py       # Sample dashboards
```

### Local URLs

| Service | URL                   |
| ------- | --------------------- |
| UI      | http://localhost:5173 |
| API     | http://localhost:8000 |

---

## Common Commands

### Running Tests

```bash
cd api
pytest                           # Run all tests
pytest --cov=. --cov-report=html # With coverage report
pytest tests/unit/               # Unit tests only
pytest -k "test_name"            # Run specific test
```

### Building for Production

```bash
cd ui
npm run build    # Build frontend
npm run preview  # Preview production build
```

### Adding UI Components

```bash
cd ui
npx shadcn@latest add <component-name>
```

### Linting

```bash
cd ui
npm run lint
```

---

## Environment Variables

### API (`api/.env`)

| Variable            | Description                      | Default                                                            |
| ------------------- | -------------------------------- | ------------------------------------------------------------------ |
| `ANTHROPIC_API_KEY` | Anthropic API key                | (required)                                                         |
| `ANTHROPIC_MODEL`   | Claude model to use              | `claude-sonnet-4-5-20250929`                                       |
| `DATABASE_URL`      | Database connection string       | `postgresql+asyncpg://postgres:postgres@localhost:5432/starkiller` |
| `ENVIRONMENT`       | development, staging, production | `development`                                                      |
| `DEBUG`             | Enable debug mode                | `true`                                                             |
| `HOST`              | API host                         | `0.0.0.0`                                                          |
| `PORT`              | API port                         | `8000`                                                             |
| `CORS_ORIGINS`      | Allowed CORS origins             | `http://localhost:5173`                                            |

---

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details.
