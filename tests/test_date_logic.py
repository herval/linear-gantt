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

    def test_planned_project_without_start_uses_issue_created_date(self):
        """Test that planned projects without start date use issue createdAt"""
        data = {
            "id": "project-1",
            "name": "Planned Project",
            "state": "planned"
            # No startDate
        }

        issues = [
            {
                "id": "issue-1",
                "createdAt": "2024-03-10T10:00:00Z",
                "state": {"type": "unstarted"}
            },
            {
                "id": "issue-2",
                "createdAt": "2024-03-05T10:00:00Z",  # Oldest
                "state": {"type": "unstarted"}
            }
        ]

        project = Project.from_linear_data(data, issues)

        effective_start = project.get_effective_start_date()
        effective_end = project.get_effective_end_date()

        # Should use oldest issue createdAt
        assert effective_start == date(2024, 3, 5)
        # Should calculate end date from that
        assert effective_end == date(2024, 3, 5) + timedelta(days=180)


class TestVelocityBasedEndDate:
    """Tests for velocity-based end date calculation"""

    def test_velocity_calculation_basic(self):
        """Test basic velocity calculation: 3 tasks in 30 days, 6 remaining"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01"
            # No targetDate - should use velocity
        }

        # 3 completed tasks over 30 days (Jan 1 - Jan 31)
        # Velocity: 3/30 = 0.1 tasks/day
        # Remaining: 6 tasks
        # Estimate: 6 / 0.1 = 60 days from Jan 31
        issues = [
            {
                "id": "issue-1",
                "startedAt": "2024-01-01T10:00:00Z",
                "completedAt": "2024-01-10T10:00:00Z",
                "state": {"type": "completed"}
            },
            {
                "id": "issue-2",
                "startedAt": "2024-01-05T10:00:00Z",
                "completedAt": "2024-01-20T10:00:00Z",
                "state": {"type": "completed"}
            },
            {
                "id": "issue-3",
                "startedAt": "2024-01-10T10:00:00Z",
                "completedAt": "2024-01-31T10:00:00Z",
                "state": {"type": "completed"}
            },
            {"id": "issue-4", "state": {"type": "started"}},
            {"id": "issue-5", "state": {"type": "started"}},
            {"id": "issue-6", "state": {"type": "unstarted"}},
            {"id": "issue-7", "state": {"type": "unstarted"}},
            {"id": "issue-8", "state": {"type": "unstarted"}},
            {"id": "issue-9", "state": {"type": "unstarted"}},
        ]

        project = Project.from_linear_data(data, issues)

        effective_end = project.get_effective_end_date()

        # Time span: Jan 1 to Jan 31 = 30 days
        # Velocity: 3 tasks / 30 days = 0.1 tasks/day
        # Remaining: 6 tasks
        # Estimate: 6 / 0.1 = 60 days
        # End date: Jan 31 + 60 days = March 31 (2024 is leap year)
        expected_end = date(2024, 3, 31)
        assert effective_end == expected_end

    def test_velocity_calculation_all_completed(self):
        """Test velocity calculation when all tasks are completed"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01"
        }

        issues = [
            {
                "id": "issue-1",
                "startedAt": "2024-01-01T10:00:00Z",
                "completedAt": "2024-01-10T10:00:00Z",
                "state": {"type": "completed"}
            },
            {
                "id": "issue-2",
                "startedAt": "2024-01-05T10:00:00Z",
                "completedAt": "2024-01-20T10:00:00Z",
                "state": {"type": "completed"}
            }
        ]

        project = Project.from_linear_data(data, issues)

        effective_end = project.get_effective_end_date()

        # All tasks completed, should use latest completion date
        assert effective_end == date(2024, 1, 20)

    def test_velocity_calculation_no_completed_tasks(self):
        """Test velocity calculation falls back when no completed tasks"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01"
        }

        issues = [
            {"id": "issue-1", "state": {"type": "started"}},
            {"id": "issue-2", "state": {"type": "started"}},
            {"id": "issue-3", "state": {"type": "unstarted"}},
        ]

        project = Project.from_linear_data(data, issues)

        effective_end = project.get_effective_end_date()

        # No completed tasks, should fall back to start + 6 months
        # Start is Jan 1 (oldest issue date would be used, but no dates)
        # Falls back to project start date
        expected_end = date(2024, 1, 1) + timedelta(days=180)
        assert effective_end == expected_end

    def test_velocity_calculation_only_planned_projects(self):
        """Test that planned projects don't use velocity calculation"""
        data = {
            "id": "project-1",
            "name": "Planned Project",
            "state": "planned",
            "startDate": "2024-01-01"
        }

        issues = [
            {
                "id": "issue-1",
                "createdAt": "2024-01-01T10:00:00Z",
                "completedAt": "2024-01-10T10:00:00Z",
                "state": {"type": "completed"}
            },
            {"id": "issue-2", "state": {"type": "unstarted"}},
            {"id": "issue-3", "state": {"type": "unstarted"}},
        ]

        project = Project.from_linear_data(data, issues)

        effective_end = project.get_effective_end_date()

        # Planned projects should use start + 6 months, not velocity
        expected_end = date(2024, 1, 1) + timedelta(days=180)
        assert effective_end == expected_end

    def test_velocity_calculation_with_target_date_set(self):
        """Test that projects with target date don't use velocity"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01",
            "targetDate": "2024-06-30"  # Has target date
        }

        issues = [
            {
                "id": "issue-1",
                "startedAt": "2024-01-01T10:00:00Z",
                "completedAt": "2024-01-10T10:00:00Z",
                "state": {"type": "completed"}
            },
            {"id": "issue-2", "state": {"type": "started"}},
            {"id": "issue-3", "state": {"type": "started"}},
        ]

        project = Project.from_linear_data(data, issues)

        effective_end = project.get_effective_end_date()

        # Should use target date, not velocity calculation
        assert effective_end == date(2024, 6, 30)

    def test_velocity_calculation_fast_velocity(self):
        """Test velocity calculation with fast completion rate"""
        data = {
            "id": "project-1",
            "name": "In Progress Project",
            "state": "started",
            "startDate": "2024-01-01"
        }

        # 5 tasks completed in 10 days (Jan 1 - Jan 11)
        # Velocity: 5/10 = 0.5 tasks/day
        # Remaining: 2 tasks
        # Estimate: 2 / 0.5 = 4 days
        issues = [
            {
                "id": "issue-1",
                "startedAt": "2024-01-01T10:00:00Z",
                "completedAt": "2024-01-03T10:00:00Z",
                "state": {"type": "completed"}
            },
            {
                "id": "issue-2",
                "startedAt": "2024-01-02T10:00:00Z",
                "completedAt": "2024-01-05T10:00:00Z",
                "state": {"type": "completed"}
            },
            {
                "id": "issue-3",
                "startedAt": "2024-01-03T10:00:00Z",
                "completedAt": "2024-01-08T10:00:00Z",
                "state": {"type": "completed"}
            },
            {
                "id": "issue-4",
                "startedAt": "2024-01-04T10:00:00Z",
                "completedAt": "2024-01-10T10:00:00Z",
                "state": {"type": "completed"}
            },
            {
                "id": "issue-5",
                "startedAt": "2024-01-05T10:00:00Z",
                "completedAt": "2024-01-11T10:00:00Z",
                "state": {"type": "completed"}
            },
            {"id": "issue-6", "state": {"type": "started"}},
            {"id": "issue-7", "state": {"type": "unstarted"}},
        ]

        project = Project.from_linear_data(data, issues)

        effective_end = project.get_effective_end_date()

        # Time span: Jan 1 to Jan 11 = 10 days
        # Velocity: 5 tasks / 10 days = 0.5 tasks/day
        # Remaining: 2 tasks
        # Estimate: 2 / 0.5 = 4 days
        # End date: Jan 11 + 4 days = Jan 15
        expected_end = date(2024, 1, 15)
        assert effective_end == expected_end
