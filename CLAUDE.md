# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Starkiller is an experimental Generative BI (Business Intelligence) tool that uses LLMs to generate data visualizations from natural language queries. Users ask questions about their data and receive dynamic, AI-generated visualizations in real-time.

## Development Commands

### Full Stack (Docker)
```bash
docker compose up --build              # Start all services (UI: 3000, API: 8000, DB: 5432)
docker compose run --rm api alembic upgrade head  # Run migrations in Docker
```

### Frontend (UI)
```bash
npm run dev      # Start dev server (port 5173)
npm run build    # Build for production (runs tsc then vite build)
npm run lint     # Run ESLint
npm run preview  # Preview production build
```

### Backend (API)
```bash
cd api
source .venv/bin/activate             # Activate virtualenv
pip install -e ".[dev]"               # Install with dev dependencies
uvicorn main:app --reload             # Start dev server (port 8000)
alembic upgrade head                  # Run migrations
pytest                                # Run tests
pytest --cov=. --cov-report=html      # Run tests with coverage
pytest tests/unit/test_specific.py   # Run specific test file
pytest -k "test_name"                 # Run tests matching pattern
```

### Database Seeding
```bash
cd api
export ADMIN_DB_URL=postgresql://postgres:postgres@localhost:5432/postgres
python scripts/seed_connection_data.py  # Create external sample databases
python scripts/seed_data_sources.py     # Populate app with sample data sources
python scripts/seed_dashboards.py       # Create sample dashboards (requires data sources)
```

## Architecture

### Monorepo Structure
- **`/ui`** - React frontend (Vite, TypeScript, Tailwind, Shadcn/ui, Recharts)
- **`/api`** - Python FastAPI backend (SQLAlchemy, Alembic, Anthropic Claude)
- Root `package.json` is a workspace delegating to `/ui`

### Backend Architecture (api/)
```
api/
├── main.py              # FastAPI app factory, lifespan, router registration
├── config.py            # Pydantic Settings for environment config
├── dependencies.py      # FastAPI dependency injection
├── core/                # Database, logging, exceptions
├── models/              # SQLAlchemy ORM models (data_source, query, visualization, dashboard)
├── schemas/             # Pydantic request/response models
├── routes/              # API endpoints (health, query, data_sources, dashboards)
├── services/            # Business logic
│   ├── data/            # Data processing with Pandas
│   ├── llm/             # LLM provider abstraction (Anthropic Claude)
│   ├── generation/      # Dashboard/visualization code generation orchestration
│   ├── query/           # SQL query execution
│   └── visualization/   # Visualization generation
├── migrations/          # Alembic database migrations
└── tests/               # pytest tests (unit/, integration/)
```

### Frontend Architecture (ui/)
```
ui/src/
├── App.tsx              # Root component with ThemeProvider, ErrorBoundary
├── components/
│   ├── ui/              # Shadcn/ui primitives (button, card, etc.)
│   ├── layout/          # Header, MainContent
│   ├── dashboards/      # Dashboard display components
│   ├── data-sources/    # Data source management UI
│   ├── dynamic/         # Dynamically rendered LLM-generated components
│   ├── query/           # Query input components
│   └── visualizations/  # Chart/visualization components
├── hooks/               # React hooks (useDashboards, useDataSources, useDashboardGeneration)
├── lib/
│   ├── api/             # API client (client.ts, dashboards.ts, data-sources.ts, query.ts)
│   ├── types/           # TypeScript type definitions
│   └── utils.ts         # cn() helper for Tailwind class merging
└── context/             # React context providers
```

### Key Data Flow
1. User enters natural language query in UI
2. Frontend calls `/api/v1/query` or `/api/v1/dashboards/generate`
3. Backend `generation/orchestrator.py` coordinates LLM calls via `services/llm/anthropic.py`
4. LLM generates React/Recharts code for visualization
5. Generated code is rendered dynamically in the frontend via `react-live`

### API Routes
- `GET/POST /api/v1/health` - Health and readiness checks
- `POST /api/v1/query` - Process natural language query
- `GET /api/v1/query/history` - Query history
- `CRUD /api/v1/data-sources` - Data source management
- `POST /api/v1/data-sources/{id}/test` - Test connection
- `GET/POST /api/v1/dashboards` - Dashboard CRUD and generation

## Code Style

### Backend (Python)
- Python 3.11+, strict typing
- SQLAlchemy 2.0 async patterns
- Pydantic v2 for validation
- pytest with asyncio_mode="auto"
- Black for formatting (line-length 88)
- Ruff for linting

### Frontend (TypeScript/React)
- React 19 with functional components and hooks
- Strict TypeScript, avoid `any`
- Tailwind CSS with utility-first approach
- Shadcn/ui for components (components live in `ui/src/components/ui/`)
- Use `cn()` from `lib/utils.ts` for conditional classes
- **File/folder naming**: Use kebab-case for all files and folders
  - Components: `some-component.tsx` with export `SomeComponent`
  - Hooks: `some-hook.ts` with export `useSomeHook`
  - Exception: `App.tsx` keeps PascalCase filename

### Adding Shadcn Components
```bash
cd ui
npx shadcn@latest add <component-name>
```

## Environment Variables

API requires `ANTHROPIC_API_KEY` in `.env`. Copy from `.env.example`:
```bash
cd api && cp .env.example .env
```

Key variables: `DATABASE_URL`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `CORS_ORIGINS`
