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

### Frontend

- **React 19** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling (dark mode default)
- **shadcn/ui** for accessible UI components
- **Recharts** for data visualization

### Backend

- **Python FastAPI**: High-performance async API framework
- **SQLAlchemy**: Async ORM with SQLite/PostgreSQL support
- **Anthropic Claude**: Primary LLM provider for query generation
- **Pandas/NumPy**: Data processing and manipulation
- **Alembic**: Database migrations
- **Pydantic**: Request/response validation

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+
- Python 3.11+
- An Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/starkiller.git
cd starkiller
```

### Running with Docker

You can run the entire stack (API, UI, Database) using Docker Compose:

```bash
docker compose up --build
```

- **UI**: http://localhost:3000 (proxies API requests to backend)
- **API**: http://localhost:8000
- **Database**: Port 5432

### Backend Setup

```bash
# Navigate to the API directory
cd api

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template and configure
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Start the API server:

```bash
uvicorn main:app --reload
```

The API will be available at:

- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

```bash
# From the project root, navigate to UI
cd ui

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:5173

### Running Both Services

For full functionality, run both the API and frontend in separate terminals:

**Terminal 1 (API):**

```bash
cd api
source .venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 (Frontend):**

```bash
cd ui
npm run dev
```

### Build

```bash
# Build frontend for production
cd ui
npm run build

# Preview production build
npm run preview
```

### Running Tests

```bash
# API tests
cd api
pytest

# With coverage
pytest --cov=. --cov-report=html
```

### Adding UI Components

shadcn/ui components can be added as needed:

```bash
cd ui
npx shadcn@latest add <component-name>
```

## API Endpoints

| Method | Endpoint                         | Description                    |
| ------ | -------------------------------- | ------------------------------ |
| GET    | `/api/v1/health`                 | Health check                   |
| GET    | `/api/v1/health/ready`           | Readiness check (DB, LLM)      |
| POST   | `/api/v1/query`                  | Process natural language query |
| GET    | `/api/v1/query/history`          | Get query history              |
| POST   | `/api/v1/data-sources`           | Create data source             |
| GET    | `/api/v1/data-sources`           | List data sources              |
| GET    | `/api/v1/data-sources/{id}`      | Get data source                |
| PATCH  | `/api/v1/data-sources/{id}`      | Update data source             |
| DELETE | `/api/v1/data-sources/{id}`      | Delete data source             |
| POST   | `/api/v1/data-sources/{id}/test` | Test connection                |

## Environment Variables

### API (.env)

| Variable            | Description                      | Default                             |
| ------------------- | -------------------------------- | ----------------------------------- |
| `ENVIRONMENT`       | development, staging, production | development                         |
| `DEBUG`             | Enable debug mode                | true                                |
| `HOST`              | API host                         | 0.0.0.0                             |
| `PORT`              | API port                         | 8000                                |
| `CORS_ORIGINS`      | Allowed CORS origins             | http://localhost:5173               |
| `DATABASE_URL`      | Database connection string       | sqlite+aiosqlite:///./starkiller.db |
| `ANTHROPIC_API_KEY` | Anthropic API key                | (required)                          |
| `ANTHROPIC_MODEL`   | Claude model to use              | claude-sonnet-4-5-20250929          |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details.
