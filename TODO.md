## Development Phases

### Phase 1: Foundation & MVP (Week 1-2)

#### Project Setup
- [ ] Create project folder structure per spec:
  - [ ] `config/settings.py`
  - [ ] `src/api/` (linear_client.py, queries.py)
  - [ ] `src/models/` (issue.py, project.py)
  - [ ] `src/visualization/` (gantt.py, formatters.py)
  - [ ] `src/utils/` (cache.py, auth.py, export.py)
  - [ ] `src/ui/` (sidebar.py, filters.py, components.py)
  - [ ] `tests/`
- [ ] Create `requirements.txt` with all dependencies from spec
- [ ] Create `.env.example` template with LINEAR_API_KEY and CACHE_TTL
- [ ] Set up basic `app.py` with Streamlit skeleton

#### Authentication & API Client
- [ ] Implement Linear API authentication (src/utils/auth.py)
- [ ] Create Linear API client (src/api/linear_client.py)
- [ ] Implement GraphQL query builder (src/api/queries.py)
- [ ] Add environment variable loading with python-dotenv
- [ ] Validate API key on startup

#### Data Models & Fetching
- [ ] Create Project data model (src/models/project.py)
  - [ ] Include: id, name, state, startDate, targetDate, progress %
  - [ ] Support for dependencies (blocked by, blocks)
- [ ] Create Issue data model (src/models/issue.py)
- [ ] Implement GraphQL query to fetch all Projects
- [ ] Calculate project % completion from issues
- [ ] Basic error handling and loading states

#### Basic Gantt Visualization
- [ ] Build Gantt chart generator (src/visualization/gantt.py)
- [ ] Render PROJECTS (not issues) as Gantt bars using Plotly
- [ ] Use project completion date as end date
- [ ] Display project % completion on bars
- [ ] Implement status color coding (Todo: Gray, In Progress: Blue, Done: Green, Cancelled: Red)
- [ ] Implement priority color coding (Urgent: Red, High: Orange, Medium: Yellow, Low: Green)
- [ ] Add basic hover tooltips with project details

### Phase 2: Core Features & Interactions (Week 3-4)

#### Dependencies & Relationships
- [ ] Link projects based on dependencies (blocked by, blocks, etc)
- [ ] Display project dependencies with connecting lines on Gantt chart
- [ ] Handle circular dependency detection

#### Filtering & Grouping
- [ ] Add project selection filter
- [ ] Implement grouping options:
  - [ ] By project
  - [ ] By assignee
  - [ ] By status
  - [ ] By cycle/sprint
  - [ ] By label
- [ ] Add date range filtering
- [ ] Create filter UI components (src/ui/filters.py)
- [ ] Create sidebar components (src/ui/sidebar.py)

#### Caching & Performance
- [ ] Implement data caching with @st.cache_data (src/utils/cache.py)
- [ ] Set up configurable cache TTL
- [ ] Add manual refresh button
- [ ] Implement optional auto-refresh with periodic sync

#### Enhanced Visualization
- [ ] Add "Today" indicator line
- [ ] Add weekend/holiday shading
- [ ] Enhance tooltips with full project details
- [ ] Improve UI/UX with better layouts and spacing

### Phase 3: Advanced Features (Week 5-6)

#### Interactive Controls
- [ ] Implement zoom in/out on timeline
- [ ] Add pan controls across timeline
- [ ] Click to view full project/issue details
- [ ] Consider drag-to-adjust dates (if write access implemented)

#### Export Functionality
- [ ] Implement export utilities (src/utils/export.py)
- [ ] Add PNG export for Gantt charts
- [ ] Add CSV export for project data
- [ ] Optional: Excel export with openpyxl

#### Visual Enhancements
- [ ] Add progress bars for in-progress projects
- [ ] Support for custom visual indicators
- [ ] Implement reusable UI components (src/ui/components.py)
- [ ] Optional: streamlit-aggrid for enhanced data tables

#### Rate Limiting & Pagination
- [ ] Implement exponential backoff for API calls
- [ ] Add pagination for large datasets
- [ ] Lazy load issues (fetch on-demand)
- [ ] Optimize API calls to stay under 1000 req/hour limit

### Phase 4: Polish & Optimization (Week 7-8)

#### Performance & Scale
- [ ] Performance optimization for large datasets (50-500 issues)
- [ ] Ensure page load time < 3 seconds
- [ ] Ensure API response time < 2 seconds
- [ ] Minimize API calls with smart refresh logic

#### Testing
- [ ] Unit tests for Linear API client (tests/test_api.py)
- [ ] Unit tests for data transformation utilities
- [ ] Integration tests for end-to-end API communication
- [ ] Visual tests for chart rendering (tests/test_visualization.py)
- [ ] Utility tests (tests/test_utils.py)

#### Security & Error Handling
- [ ] Comprehensive error handling throughout app
- [ ] Validate all user inputs
- [ ] Ensure API keys never committed to version control
- [ ] Implement read-only mode (no write operations)
- [ ] Security audit for API key handling

#### Documentation & Deployment
- [ ] Create user documentation
- [ ] Add inline code documentation
- [ ] Create README with setup instructions
- [ ] Configure for Streamlit Cloud deployment
- [ ] Optional: Create Docker configuration
- [ ] Final bug fixes and testing

#### Nice-to-Have
- [ ] Responsive design improvements (mobile/tablet)
- [ ] Analytics features
- [ ] Support for Linear custom fields
- [ ] Configuration persistence across sessions
