# Development Methodology for Linear Gantt Chart Visualizer

This document outlines the development practices and methodology for maintaining this project.

## Core Principles

1. **Test-Driven Development**: Write tests before or alongside code changes
2. **Clean Commits**: Commit working, tested code at stable milestones
3. **Documentation**: Keep README, TODO, and PROJECT_SPEC in sync
4. **Code Reuse**: Follow DRY principles and maintain modular architecture
5. **Scope Discipline**: Never modify files outside this working directory

---

## Testing Requirements

### MANDATORY: Tests for Every Change

**Before writing code:**
1. Understand what you're changing and what could break
2. Identify which test file(s) need updates
3. Write failing tests first (TDD approach when possible)

**After writing code:**
1. Run relevant test suite: `python -m pytest tests/test_<module>.py -v`
2. Run ALL tests before committing: `python -m pytest tests/ -v`
3. Ensure ALL tests pass (no exceptions)
4. Add new tests for new functionality

### Test Coverage Areas

- **`tests/test_models.py`**: Project and Issue data models
- **`tests/test_date_logic.py`**: Smart date calculation, velocity-based estimates
- **`tests/test_visualization.py`**: Gantt chart rendering logic
- **`tests/test_api.py`**: Linear API client and authentication
- **`tests/test_app.py`**: Streamlit application logic

### Test Writing Guidelines

```python
# Good: Descriptive test names
def test_velocity_calculation_with_3_completed_tasks_estimates_60_days():
    """Test basic velocity calculation: 3 tasks in 30 days, 6 remaining"""
    # Arrange
    data = {...}
    # Act
    result = project.get_effective_end_date()
    # Assert
    assert result == expected_date

# Good: Test edge cases
def test_velocity_calculation_falls_back_when_no_completed_tasks():
    """Test velocity calculation falls back to start + 6 months"""
    ...
```

---

## Development Workflow

### 1. Planning Phase

**Use TodoWrite tool to plan tasks:**
```python
TodoWrite({
    "todos": [
        {"content": "Add feature X", "status": "in_progress", "activeForm": "Adding feature X"},
        {"content": "Write tests for X", "status": "pending", "activeForm": "Writing tests for X"},
        {"content": "Update docs", "status": "pending", "activeForm": "Updating docs"},
        {"content": "Commit changes", "status": "pending", "activeForm": "Committing changes"}
    ]
})
```

**Break down complex tasks:**
- If a task has 3+ steps, break it into smaller tasks
- Mark tasks as in_progress → completed as you go
- Keep TODO list in sync with actual progress

### 2. Implementation Phase

**Order of operations:**
1. Read relevant source files
2. Write/update tests (if TDD approach)
3. Implement the feature/fix
4. Run tests and iterate until passing
5. Update TodoWrite to mark task completed

**Code organization:**
- **Models** (`src/models/`): Data structures, business logic
- **API** (`src/api/`): Linear API client, GraphQL queries
- **Visualization** (`src/visualization/`): Gantt chart rendering
- **Utils** (`src/utils/`): Caching, authentication, helpers
- **Config** (`config/`): Settings, constants, color schemes

### 3. Testing Phase

**Run tests progressively:**
```bash
# Test the specific module you changed
python -m pytest tests/test_models.py -v

# Run all tests before committing
python -m pytest tests/ -v

# Check test coverage (optional but encouraged)
python -m pytest tests/ --cov=src --cov-report=term-missing
```

**What to test:**
- Happy path (normal usage)
- Edge cases (empty data, None values, missing fields)
- Error handling (invalid input, API errors)
- Backward compatibility (cached data, old project structures)

### 4. Commit Phase

**Only commit when:**
- ✅ All tests pass
- ✅ Code is working and tested
- ✅ TODO list is updated
- ✅ Changes are at a stable milestone

**Commit message format:**
```
Brief summary of changes (imperative mood)

Detailed description of what changed and why:
- Added X feature to handle Y scenario
- Updated Z to support new functionality
- Fixed bug where A would cause B

Technical details:
- Modified file1.py: added method_x()
- Updated file2.py: changed logic in method_y()
- Added tests in test_file.py

All N tests passing.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Git workflow:**
```bash
# Check status
git status

# Review changes
git diff <files>

# Stage files
git add <files>

# Commit with detailed message
git commit -m "$(cat <<'EOF'
Your detailed commit message here
EOF
)"

# Verify commit
git log --oneline -1
```

---

## Streamlit-Specific Considerations

### Caching

**Important:** Streamlit caches function results. When adding new fields to models:

1. **Update the model** (e.g., add `team_names` field)
2. **Add defensive checks** for cached objects:
   ```python
   # Good: Backward compatible with cached data
   team_names = getattr(project, 'team_names', [])

   # Bad: Will break with cached objects
   team_names = project.team_names
   ```
3. **Test with cache clear**: User can click "Refresh Data" to clear cache

### Function Signatures

**Cache-friendly function signatures:**
```python
# Good: Underscore prefix tells Streamlit not to hash
@st.cache_data
def fetch_projects(_client: LinearClient):
    ...

# Bad: Will cause UnhashableParamError
@st.cache_data
def fetch_projects(client: LinearClient):
    ...
```

---

## Code Quality Standards

### Error Handling

**Always handle potential failures:**
```python
# Good: Defensive error handling
try:
    date_obj = datetime.fromisoformat(date_str).date()
except (ValueError, TypeError):
    date_obj = None

# Good: Informative error messages
if not api_key:
    st.error("⚠️ LINEAR_API_KEY not found. Please set it in your .env file.")
    st.info("Copy .env.example to .env and add your Linear API key")
    st.stop()
```

### Type Hints

**Use type hints for clarity:**
```python
from typing import Optional, List, Dict

def get_effective_end_date(self) -> Optional[date]:
    """Calculate effective end date"""
    ...

def filter_projects_by_date_range(
    projects: List[Dict],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict]:
    ...
```

### Documentation

**Docstrings for all public methods:**
```python
def _calculate_velocity_based_end_date(self) -> Optional[date]:
    """
    Calculate end date based on velocity of completed issues

    Logic:
    1. Find the time span from earliest start to latest completion of completed issues
    2. Calculate velocity (completed issues per day)
    3. Estimate remaining time based on open issues
    4. Return latest completion date + estimated remaining time

    Returns:
        date: Estimated end date or None if not enough data
    """
    ...
```

---

## Feature Development Checklist

When adding a new feature, follow this checklist:

### Planning
- [ ] Create TodoWrite plan with all steps
- [ ] Read PROJECT_SPEC.md to ensure alignment
- [ ] Check TODO.md for related tasks
- [ ] Identify which files need changes
- [ ] Identify which tests need updates

### GraphQL/API Changes
- [ ] Update query in `src/api/queries.py`
- [ ] Test query returns expected data structure
- [ ] Handle pagination if needed
- [ ] Add error handling for API failures

### Model Changes
- [ ] Update data model in `src/models/`
- [ ] Add new fields to `from_linear_data()` method
- [ ] Update `to_gantt_dict()` if Gantt needs the data
- [ ] Add backward compatibility for cached objects
- [ ] Write tests for new model logic

### Visualization Changes
- [ ] Update `src/visualization/gantt.py`
- [ ] Test chart renders correctly
- [ ] Check performance with many projects
- [ ] Ensure responsive design (use_container_width)

### UI Changes
- [ ] Update `app.py` with new UI elements
- [ ] Add appropriate filters/controls
- [ ] Test with different data scenarios
- [ ] Ensure mobile responsiveness

### Testing
- [ ] Write unit tests for new logic
- [ ] Write integration tests if needed
- [ ] Test edge cases and error conditions
- [ ] Run all tests: `python -m pytest tests/ -v`
- [ ] Verify all tests pass

### Documentation
- [ ] Update README.md if user-facing
- [ ] Update TODO.md with completed tasks
- [ ] Add docstrings to new functions
- [ ] Update PROJECT_SPEC.md if architecture changed

### Commit
- [ ] Review all changes: `git diff`
- [ ] Stage relevant files only
- [ ] Write detailed commit message
- [ ] Update TodoWrite to mark all tasks completed

---

## Common Patterns

### Adding a New Filter

1. **Fetch data** (if needed): Update GraphQL query
2. **Process data**: Extract filter options in app.py
3. **UI controls**: Add checkboxes/selectboxes in sidebar
4. **Filter logic**: Apply filter to projects list
5. **Propagate**: Use filtered_projects throughout
6. **Test**: Verify filter works with all combinations

### Adding Smart Date Logic

1. **Model method**: Add calculation method in Project model
2. **Integrate**: Call from `get_effective_end_date()` or similar
3. **Test extensively**: Write 5-10 tests covering edge cases
4. **Document**: Add clear docstring explaining logic

### Adding Visualization Feature

1. **Data preparation**: Ensure data in `to_gantt_dict()`
2. **Chart logic**: Update `create_gantt_chart()` in gantt.py
3. **Plotly traces**: Add new scatter/annotation/shape traces
4. **Toggle control**: Add checkbox in sidebar if optional
5. **Test**: Verify rendering and interactions

---

## File Modification Guidelines

### DO:
- ✅ Modify files in `src/`, `tests/`, `config/`
- ✅ Update `app.py`, `requirements.txt`, `README.md`
- ✅ Create new test files in `tests/`
- ✅ Update `.env.example` if adding new env vars

### DON'T:
- ❌ Modify files outside project directory
- ❌ Change `.gitignore` without good reason
- ❌ Commit `.env` (keep secrets local)
- ❌ Remove existing tests without replacement
- ❌ Break backward compatibility without migration plan

---

## Performance Considerations

### Streamlit Performance
- Use `@st.cache_data` for expensive operations
- Clear cache with "Refresh Data" button
- Avoid deep nesting in component trees
- Use `st.expander` for debug/verbose output

### Plotly Performance
- Dynamic height based on number of projects
- Limit traces for large datasets
- Use efficient data structures (lists/dicts, not complex objects)

### API Performance
- Batch requests when possible
- Handle pagination properly
- Cache API responses
- Implement rate limiting respect

---

## Debugging Workflow

### When Things Break

1. **Read the error**: Full traceback tells you where/what failed
2. **Check tests**: Run test suite to isolate issue
3. **Add debug output**: Use `st.expander("🔍 Debug: ...")` for inspection
4. **Verify data**: Check what Linear API actually returns
5. **Clear cache**: Click "Refresh Data" to eliminate stale cache
6. **Reproduce**: Create minimal test case that reproduces issue
7. **Fix and test**: Fix the bug, add regression test
8. **Remove debug**: Clean up debug output before committing

### Common Issues

**AttributeError on Project objects:**
- Likely cached data before field was added
- Add `getattr(obj, 'field', default)` for compatibility
- Document in commit message

**Tests failing after model change:**
- Update test data to match new structure
- Check that all model tests pass
- Verify `from_linear_data()` handles new fields

**Gantt chart not rendering:**
- Check browser console for errors
- Verify data has `start` and `end` dates
- Check Plotly trace structure
- Ensure data types are correct (strings for dates)

---

## Summary: The Golden Rules

1. **Always write tests** - No exceptions
2. **Always run tests before committing** - `pytest tests/ -v`
3. **Always use TodoWrite** - Track your work
4. **Always commit at stable milestones** - Working, tested code only
5. **Always document your changes** - Docstrings + commit messages
6. **Always consider backward compatibility** - Cache and old data
7. **Always update TODO.md** - Keep project status current
8. **Never modify files outside this directory** - Stay in scope
9. **Never commit secrets** - Use .env, never commit it
10. **Never skip the checklist** - Quality over speed

---

## Questions?

Refer to:
- `PROJECT_SPEC.md` - Architecture and requirements
- `TODO.md` - Current project status and next tasks
- `README.md` - User-facing documentation
- Existing tests - Examples of good test patterns
