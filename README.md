# Linear Gantt Chart Visualizer

A Streamlit-based web application that integrates with the Linear API to fetch project data and visualize it as interactive Gantt charts.

## Features

- 📊 Interactive Gantt chart visualization of Linear projects
- 🔄 Real-time synchronization with Linear data
- 🎨 Color-coded status and priority indicators
- 📈 Project progress tracking
- 🔗 Dependency visualization
- 🎯 Multiple grouping and filtering options
- 🧠 **Smart date calculation:**
  - Planned projects: Uses project start date
  - In Progress projects: Uses oldest started/completed issue date
  - Missing end dates: Automatically calculates as start + 6 months

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (`brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [just](https://github.com/casey/just) (optional, for the task runner — `brew install just`)
- Linear API key ([Get one here](https://linear.app/settings/api))

uv manages the Python toolchain and virtual environment for you; the pinned Python version lives in `.python-version`.

### Installation

#### Option 1: Quick Start (Recommended)

With `just`:
```bash
just run
```

Or run the setup script directly:
```bash
./run.sh
```

Either path will automatically:
- Provision the correct Python version and virtual environment (`.venv`)
- Install all dependencies from `pyproject.toml` / `uv.lock`
- Set up your `.env` file (via `run.sh`)
- Launch the application

#### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd linear-gantt
```

2. Install dependencies (creates `.venv` automatically):
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your Linear API key:
```
LINEAR_API_KEY=your_api_key_here
CACHE_TTL=3600
```

### Running the Application

```bash
just run              # via the task runner
# or
uv run streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Managing Dependencies

```bash
uv add <package>              # add a runtime dependency
uv add --dev <package>        # add a dev/test dependency
uv sync                       # install from the lockfile
```

## Project Structure

```
linear-gantt/
├── app.py                      # Main Streamlit application
├── pyproject.toml             # Project metadata & dependencies (uv)
├── uv.lock                    # Pinned dependency lockfile
├── Justfile                   # Task runner recipes (just run/test/…)
├── .env.example               # Environment variable template
├── config/
│   └── settings.py            # Configuration management
├── src/
│   ├── api/
│   │   ├── linear_client.py   # Linear API client
│   │   └── queries.py         # GraphQL queries
│   ├── models/
│   │   ├── issue.py           # Issue data model
│   │   └── project.py         # Project data model
│   ├── visualization/
│   │   ├── gantt.py           # Gantt chart generation
│   │   └── formatters.py      # Data formatting for charts
│   ├── utils/
│   │   ├── cache.py           # Caching utilities
│   │   ├── auth.py            # Authentication helpers
│   │   └── export.py          # Export functionality
│   └── ui/
│       ├── sidebar.py         # Sidebar components
│       ├── filters.py         # Filter widgets
│       └── components.py      # Reusable UI components
└── tests/                     # Test files
```

## Configuration

### Environment Variables

- `LINEAR_API_KEY`: Your Linear Personal API Key (required)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)

### Color Schemes

The application uses the following color coding:

**Status Colors:**
- Todo: Gray (#6B7280)
- In Progress: Blue (#3B82F6)
- Done: Green (#10B981)
- Cancelled: Red (#EF4444)

**Priority Colors:**
- Urgent: Red
- High: Orange
- Medium: Yellow
- Low: Green

## Development

### Current Status

Phase 1 (Foundation & MVP) is in progress. See [TODO.md](TODO.md) for detailed task tracking.

### Status: MVP Complete ✅

All Phase 1 features have been successfully implemented:
- ✅ Project structure setup
- ✅ Configuration management
- ✅ Linear API client with rate limiting
- ✅ GraphQL queries
- ✅ Data models (Project & Issue)
- ✅ Authentication utilities
- ✅ Gantt chart visualization with Plotly
- ✅ Interactive Streamlit UI
- ✅ Date filtering and controls
- ✅ Progress tracking and metrics
- ✅ Comprehensive test suite (42 tests, 100% passing)

### Running Tests

```bash
just test
# or
uv run pytest
```

All 42 tests passing ✅

## Contributing

1. Follow the project structure defined in PROJECT_SPEC.md
2. Update TODO.md as tasks are completed
3. Ensure all tests pass before committing
4. Follow PEP 8 style guidelines

## License

[Add your license here]

## Support

For issues and questions, please check the project documentation or open an issue on GitHub.
