# Linear Gantt Chart Visualizer - Project Specification

## Project Overview

A Streamlit-based web application that integrates with the Linear API to fetch project data and visualize it as interactive Gantt charts. This tool enables project managers and teams to view Linear projects in a timeline format, track progress, identify dependencies, and manage resources effectively.

## Goals & Objectives

### Primary Goals
- Provide an intuitive Gantt chart view of Linear projects
- Enable real-time synchronization with Linear data
- Support multiple projects and teams
- Offer interactive filtering and customization options

### Success Criteria
- Successfully authenticate and fetch data from Linear API
- Render Gantt charts with issues as tasks
- Display task dependencies and relationships
- Support date range filtering and project selection
- Load and render within 3 seconds for typical projects (<200 issues)

## Core Features

### 1. Authentication & Configuration
- LINEAR_API_TOKEN defined on .env file
- No other configuration needed

### 2. Data Fetching & Management
- Retrieve all Projects
- Use the project completion date as the end date for the Gantt chart
- Link projects based on their dependencies (blocked by, blocks, etc)
- Use the % of completion to show the progress of the project on each Gantt chart element
- Represent status and priority as color coding

- **Data Caching**: Cache Linear data to reduce API calls
- **Auto-refresh**: Optional periodic data synchronization (plus a button to refresh)

### 3. Gantt Chart Visualization
- **Timeline View**: Display issues as horizontal bars on a time axis
- **Grouping Options**:
  - By project
  - By assignee
  - By status
  - By cycle/sprint
  - By label
- **Visual Indicators**:
  - Color coding by status, priority, or assignee
  - Progress bars for in-progress tasks
  - Today indicator line
  - Weekend/holiday shading
- **Dependencies**: Show project dependencies with connecting lines
- **Interactive Elements**:
  - Hover tooltips with task details
  - Click to view full issue details
  - Drag to adjust date ranges (if write access is implemented)
  - Zoom in/out on timeline
  - Pan across timeline

## Technical Stack

### Core Technologies
- **Frontend Framework**: Streamlit (Python)
- **Gantt Chart Library**:
  - Primary: Plotly (plotly.express.timeline or plotly.figure_factory.create_gantt)
  - Alternative: matplotlib-gantt or custom D3.js via Streamlit components
- **API Client**: Linear API (GraphQL)
  - Library: `requests` or `gql` for GraphQL queries
- **Data Processing**:
  - pandas (data manipulation)
  - numpy (calculations)
- **Caching**: Streamlit's `@st.cache_data` decorator

### Dependencies
```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
gql>=3.4.0
```

### Optional Dependencies
- `streamlit-aggrid`: Enhanced data tables
- `openpyxl`: Excel export support
- `matplotlib`: Alternative visualization
- `Pillow`: Image processing for exports

## Architecture

### Application Structure
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
└── tests/
    ├── test_api.py
    ├── test_visualization.py
    └── test_utils.py
```

### Data Flow
1. **Data Fetch**: App queries Linear GraphQL API for projects and issues
2. **Data Processing**: Transform Linear data into Gantt-compatible format
3. **Caching**: Store processed data in Streamlit cache
4. **Visualization**: Generate Plotly Gantt chart from processed data
5. **Interactivity**: User filters/modifies view, triggering re-render
6. **Export**: Generate static files on demand

## Linear API Integration

### Authentication
- Use Linear Personal API Key
- Store securely (environment variable or Streamlit secrets)
- Validate on startup

### GraphQL Queries

#### Fetch Projects
```graphql
query($teamId: String!) {
  team(id: $teamId) {
    projects {
      nodes {
        id
        name
        state
        startDate
        targetDate
      }
    }
  }
}
```

#### Fetch Issues
```graphql
query($projectId: String!) {
  project(id: $projectId) {
    issues {
      nodes {
        id
        title
        description
        priority
        estimate
        startedAt
        dueDate
        completedAt
        state {
          name
          type
        }
        assignee {
          name
          avatarUrl
        }
        labels {
          nodes {
            name
            color
          }
        }
        parent {
          id
        }
      }
    }
  }
}
```

### Rate Limiting
- Linear API limit: 1000 requests per hour
- Implement exponential backoff
- Cache aggressively
- Use pagination for large datasets


### Color Scheme
- **Status Colors**:
  - Todo: Gray (#6B7280)
  - In Progress: Blue (#3B82F6)
  - Done: Green (#10B981)
  - Cancelled: Red (#EF4444)
- **Priority Colors**:
  - Urgent: Red
  - High: Orange
  - Medium: Yellow
  - Low: Green

### Responsive Design
- Mobile: Vertical scrolling for Gantt chart
- Tablet: Collapsible sidebar
- Desktop: Full layout as shown


## Configuration & Deployment

### Environment Variables
```
LINEAR_API_KEY=your_api_key_here
CACHE_TTL=3600
```

### Deployment Options
1. **Streamlit Cloud**: Free tier, easy deployment from GitHub
2. **Docker**: Containerized deployment
3. **Heroku**: PaaS deployment
4. **AWS/GCP**: Cloud platform deployment

### Performance Considerations
- Lazy load issues (fetch on-demand)
- Paginate large datasets
- Use Streamlit's caching effectively
- Minimize API calls with smart refresh logic
- Consider serverless functions for API proxy

## Security Considerations

- Store API keys in environment variables or Streamlit secrets
- Never commit API keys to version control
- Implement read-only mode (no write operations to Linear)
- Validate all user inputs
- Use HTTPS for deployment
- Consider OAuth flow for multi-user deployments

## Testing Strategy

### Unit Tests
- Linear API client functions
- Data transformation utilities
- Query builders

### Integration Tests
- End-to-end API communication
- Chart rendering with sample data

### Manual Testing
- UI/UX flow testing
- Cross-browser compatibility
- Performance with various dataset sizes

## Success Metrics

- Successfully visualize projects with 50-500 issues
- Page load time < 3 seconds
- API response time < 2 seconds
- Zero API key exposure incidents
- Positive user feedback on usability

## Future Enhancements

- **Collaboration**: Multi-user support with shared views
- **Notifications**: Alerts for approaching deadlines
- **Custom Fields**: Support for Linear custom fields
- **Time Tracking**: Integration with time tracking data
- **Forecasting**: Predict project completion dates
- **Mobile App**: Native mobile experience
- **Real-time Updates**: WebSocket support for live updates
- **Templates**: Pre-configured views for common use cases
- **API Webhooks**: Auto-refresh on Linear changes
