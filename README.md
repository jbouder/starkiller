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

- **Python FastAPI**: High-performance API framework
- **LLM Integration**: OpenAI, Anthropic, or other LLM providers
- **Data Processing**: Pandas, NumPy for data manipulation

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/starkiller.git
cd starkiller

# Install dependencies
npm install
```

### Development

```bash
# Start the UI development server
npm run dev
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Adding UI Components

shadcn/ui components can be added as needed:

```bash
cd ui
npx shadcn@latest add <component-name>
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details.
