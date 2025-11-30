# Linear Gantt Chart Visualizer

A Streamlit-based web application that integrates with the Linear API to fetch project data and visualize it as interactive Gantt charts.

## Features

- 📊 Interactive Gantt chart visualization of Linear projects
- 🔄 Real-time synchronization with Linear data
- 🎨 Color-coded status and priority indicators
- 📈 Project progress tracking
- 🔗 Dependency visualization
- 🎯 Multiple grouping and filtering options
- 📅 Automatically filters to show only projects with defined start and target dates

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Linear API key ([Get one here](https://linear.app/settings/api))

### Installation

#### Option 1: Quick Start (Recommended)

Just run the setup script:
```bash
./run.sh
```

This will automatically:
- Create a virtual environment
- Install all dependencies
- Set up your `.env` file
- Launch the application

#### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd linear-gantt
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Linear API key:
```
LINEAR_API_KEY=your_api_key_here
CACHE_TTL=3600
```

### Running the Application

#### Using the run script:
```bash
./run.sh
```

#### Manual start:
```bash
source venv/bin/activate
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## Project Structure

```
linear-gantt/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
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
source venv/bin/activate
pytest tests/ -v
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
