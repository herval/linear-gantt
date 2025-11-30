"""
Tests for smart date calculation logic
"""

import pytest
from datetime import date, timedelta
from src.models.project import Project


class TestEffectiveDates:
    """Tests for effective date calculation"""

    def test_planned_project_uses_project_start_date(self):
        """Test that planned projects use the project start date"""
        data = {
            "id": "project-1",
            "name": "Planned Project",
            "state": "planned",
            "startDate": "2024-01-01",
            "targetDate": "2024-06-30"
        }

        project = Project.from_linear_data(data, [])

        effective_start = project.get_effective_start_date()
        assert effective_start == date(2024, 1, 1)

    def test_in_progress_project_uses_oldest_issue_date(self):
        """Test that in-progress projects use oldest started/completed issue date"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01",
            "targetDate": "2024-06-30"
        }

        issues = [
            {
                "id": "issue-1",
                "startedAt": "2024-02-15T10:00:00Z",
                "state": {"type": "started"}
            },
            {
                "id": "issue-2",
                "startedAt": "2024-02-10T10:00:00Z",  # Oldest
                "state": {"type": "started"}
            },
            {
                "id": "issue-3",
                "completedAt": "2024-02-20T10:00:00Z",
                "state": {"type": "completed"}
            }
        ]

        project = Project.from_linear_data(data, issues)

        effective_start = project.get_effective_start_date()
        assert effective_start == date(2024, 2, 10)

    def test_in_progress_project_falls_back_to_project_date(self):
        """Test fallback to project start date when no issues have dates"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01",
            "targetDate": "2024-06-30"
        }

        issues = [
            {"id": "issue-1", "state": {"type": "unstarted"}},
            {"id": "issue-2", "state": {"type": "backlog"}}
        ]

        project = Project.from_linear_data(data, issues)

        effective_start = project.get_effective_start_date()
        assert effective_start == date(2024, 1, 1)

    def test_end_date_uses_target_when_set(self):
        """Test that target date is used when available"""
        data = {
            "id": "project-1",
            "name": "Test Project",
            "state": "planned",
            "startDate": "2024-01-01",
            "targetDate": "2024-06-30"
        }

        project = Project.from_linear_data(data, [])

        effective_end = project.get_effective_end_date()
        assert effective_end == date(2024, 6, 30)

    def test_end_date_calculates_6_months_when_not_set(self):
        """Test that end date is calculated as start + 6 months when not set"""
        data = {
            "id": "project-1",
            "name": "Test Project",
            "state": "planned",
            "startDate": "2024-01-01"
            # No targetDate
        }

        project = Project.from_linear_data(data, [])

        effective_end = project.get_effective_end_date()
        # Start date + 180 days
        expected_end = date(2024, 1, 1) + timedelta(days=180)
        assert effective_end == expected_end

    def test_in_progress_project_with_calculated_dates(self):
        """Test full calculation for in-progress project with issues"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01"
            # No targetDate - should calculate
        }

        issues = [
            {
                "id": "issue-1",
                "startedAt": "2024-03-15T10:00:00Z",
                "state": {"type": "started"}
            }
        ]

        project = Project.from_linear_data(data, issues)

        effective_start = project.get_effective_start_date()
        effective_end = project.get_effective_end_date()

        # Should use issue start date
        assert effective_start == date(2024, 3, 15)
        # Should calculate from issue start date + 6 months
        assert effective_end == date(2024, 3, 15) + timedelta(days=180)

    def test_to_gantt_dict_uses_effective_dates(self):
        """Test that to_gantt_dict uses effective dates"""
        data = {
            "id": "project-1",
            "name": "Test Project",
            "state": "started",
            "startDate": "2024-01-01"
        }

        issues = [
            {
                "id": "issue-1",
                "startedAt": "2024-02-01T10:00:00Z",
                "state": {"type": "started"}
            }
        ]

        project = Project.from_linear_data(data, issues)
        gantt_dict = project.to_gantt_dict()

        # Should use issue date (2024-02-01), not project date (2024-01-01)
        assert gantt_dict["start"] == "2024-02-01"
        # Should calculate end as 2024-02-01 + 180 days
        expected_end = (date(2024, 2, 1) + timedelta(days=180)).isoformat()
        assert gantt_dict["end"] == expected_end

    def test_project_without_any_dates_returns_none(self):
        """Test that projects without any dates return None"""
        data = {
            "id": "project-1",
            "name": "Test Project",
            "state": "planned"
            # No dates at all
        }

        project = Project.from_linear_data(data, [])

        assert project.get_effective_start_date() is None
        assert project.get_effective_end_date() is None

    def test_in_progress_ignores_unstarted_issues(self):
        """Test that only started/completed issues are considered"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01"
        }

        issues = [
            {
                "id": "issue-1",
                "state": {"type": "backlog"}  # Should be ignored
            },
            {
                "id": "issue-2",
                "state": {"type": "unstarted"}  # Should be ignored
            },
            {
                "id": "issue-3",
                "startedAt": "2024-02-15T10:00:00Z",
                "state": {"type": "started"}  # Should be used
            }
        ]

        project = Project.from_linear_data(data, issues)

        effective_start = project.get_effective_start_date()
        assert effective_start == date(2024, 2, 15)
