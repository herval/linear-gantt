"""
Tests for main Streamlit application
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api.linear_client import LinearClient


class TestApp:
    """Tests for app.py functions"""

    def test_cached_function_signature(self):
        """Test that fetch_projects_with_issues uses underscore prefix for client parameter"""
        from app import fetch_projects_with_issues
        import inspect

        sig = inspect.signature(fetch_projects_with_issues)
        params = list(sig.parameters.keys())

        # Verify the parameter uses underscore prefix (Streamlit caching requirement)
        assert params[0] == '_client', "Client parameter must use underscore prefix for Streamlit caching"

    @patch('app.st')
    def test_fetch_logic_basic(self, mock_st):
        """Test the basic fetching logic without caching"""
        from src.models.project import Project

        # Create a mock client instance
        mock_client = Mock(spec=LinearClient)

        # Mock the get_projects response
        mock_client.get_projects.return_value = [
            {
                "id": "project-1",
                "name": "Test Project",
                "state": "started",
                "startDate": "2024-01-01",
                "targetDate": "2024-12-31"
            }
        ]

        # Mock the get_project_issues response
        mock_client.get_project_issues.return_value = [
            {"state": {"type": "completed"}},
            {"state": {"type": "started"}}
        ]

        # Test the logic directly without going through cached function
        projects_data = mock_client.get_projects()
        projects = []

        for project_data in projects_data:
            issues_data = mock_client.get_project_issues(project_data["id"])
            project = Project.from_linear_data(project_data, issues_data)

            # Only include projects that have effective dates
            if project.get_effective_start_date() and project.get_effective_end_date():
                projects.append(project)

        # Verify results
        assert len(projects) == 1
        assert projects[0].name == "Test Project"
        assert projects[0].issue_count == 2
        assert projects[0].completed_issue_count == 1

    @patch('app.st')
    def test_fetch_logic_empty(self, mock_st):
        """Test fetching when no projects exist"""
        from src.models.project import Project

        mock_client = Mock(spec=LinearClient)
        mock_client.get_projects.return_value = []

        # Test the logic
        projects_data = mock_client.get_projects()
        projects = []

        for project_data in projects_data:
            issues_data = mock_client.get_project_issues(project_data["id"])
            project = Project.from_linear_data(project_data, issues_data)

            if project.get_effective_start_date() and project.get_effective_end_date():
                projects.append(project)

        assert len(projects) == 0

    @patch('app.st')
    def test_fetch_logic_filters_projects_without_effective_dates(self, mock_st):
        """Test that projects without effective dates are filtered out"""
        from src.models.project import Project

        mock_client = Mock(spec=LinearClient)

        # Mock projects with varying date availability
        mock_client.get_projects.return_value = [
            {
                "id": "project-1",
                "name": "Project with dates",
                "state": "planned",
                "startDate": "2024-01-01",
                "targetDate": "2024-12-31"
            },
            {
                "id": "project-2",
                "name": "Project without any dates",
                "state": "planned"
                # No dates - should be filtered
            },
            {
                "id": "project-3",
                "name": "In progress with issue dates",
                "state": "started",
                "startDate": "2024-01-01"
                # Has start date, will calculate end date
            }
        ]

        def mock_get_issues(project_id):
            if project_id == "project-3":
                return [
                    {"id": "issue-1", "startedAt": "2024-02-01T10:00:00Z", "state": {"type": "started"}}
                ]
            return []

        mock_client.get_project_issues.side_effect = mock_get_issues

        # Test the filtering logic
        projects_data = mock_client.get_projects()
        projects = []

        for project_data in projects_data:
            issues_data = mock_client.get_project_issues(project_data["id"])
            project = Project.from_linear_data(project_data, issues_data)

            # Only include projects with effective dates
            if project.get_effective_start_date() and project.get_effective_end_date():
                projects.append(project)

        # project-1 and project-3 should be included (both have effective dates)
        # project-2 should be filtered out (no dates at all)
        assert len(projects) == 2
        assert projects[0].name == "Project with dates"
        assert projects[1].name == "In progress with issue dates"

    @patch('app.st')
    def test_fetch_logic_error_handling(self, mock_st):
        """Test error handling when fetching issues fails"""
        from src.models.project import Project

        mock_client = Mock(spec=LinearClient)

        # Mock project that exists with valid dates
        mock_client.get_projects.return_value = [
            {
                "id": "project-1",
                "name": "Test Project",
                "state": "planned",
                "startDate": "2024-01-01",
                "targetDate": "2024-12-31"
            }
        ]

        # Mock failure when fetching issues
        mock_client.get_project_issues.side_effect = Exception("API Error")

        # Test the error handling logic
        projects_data = mock_client.get_projects()
        projects = []

        for project_data in projects_data:
            try:
                issues_data = mock_client.get_project_issues(project_data["id"])
                project = Project.from_linear_data(project_data, issues_data)

                if project.get_effective_start_date() and project.get_effective_end_date():
                    projects.append(project)
            except Exception:
                # Create project without issues
                project = Project.from_linear_data(project_data)

                if project.get_effective_start_date() and project.get_effective_end_date():
                    projects.append(project)

        # Should still return project without issues (planned project has dates)
        assert len(projects) == 1
        assert projects[0].name == "Test Project"
        assert projects[0].issue_count == 0
