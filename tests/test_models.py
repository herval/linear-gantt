"""
Tests for data models
"""

import pytest
from datetime import datetime, date
from src.models.project import Project
from src.models.issue import Issue, IssueState, Assignee, IssueLabel


class TestProject:
    """Tests for Project model"""

    def test_from_linear_data_basic(self):
        """Test creating Project from basic Linear data"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "started"
        }

        project = Project.from_linear_data(data)

        assert project.id == "project-123"
        assert project.name == "Test Project"
        assert project.state == "started"
        assert project.progress == 0.0

    def test_from_linear_data_with_dates(self):
        """Test creating Project with dates"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "started",
            "startDate": "2024-01-01",
            "targetDate": "2024-12-31"
        }

        project = Project.from_linear_data(data)

        assert project.start_date == date(2024, 1, 1)
        assert project.target_date == date(2024, 12, 31)

    def test_from_linear_data_with_issues(self):
        """Test creating Project with issues for progress calculation"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "started"
        }

        issues = [
            {"state": {"type": "completed"}},
            {"state": {"type": "completed"}},
            {"state": {"type": "started"}},
            {"state": {"type": "unstarted"}}
        ]

        project = Project.from_linear_data(data, issues)

        assert project.issue_count == 4
        assert project.completed_issue_count == 2
        assert project.progress == 50.0

    def test_get_status_completed(self):
        """Test status for completed project"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "completed"
        }

        project = Project.from_linear_data(data)
        assert project.get_status() == "done"

    def test_get_status_in_progress(self):
        """Test status for in-progress project"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "started"
        }

        project = Project.from_linear_data(data)
        assert project.get_status() == "in_progress"

    def test_get_status_cancelled(self):
        """Test status for cancelled project"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "cancelled"
        }

        project = Project.from_linear_data(data)
        assert project.get_status() == "cancelled"

    def test_get_duration_days(self):
        """Test duration calculation"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "started",
            "startDate": "2024-01-01",
            "targetDate": "2024-01-31"
        }

        project = Project.from_linear_data(data)
        assert project.get_duration_days() == 30

    def test_is_overdue(self):
        """Test overdue detection"""
        # Past date, not completed
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "started",
            "targetDate": "2020-01-01"
        }

        project = Project.from_linear_data(data)
        assert project.is_overdue() is True

    def test_to_gantt_dict(self):
        """Test conversion to Gantt chart format"""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "state": "started",
            "startDate": "2024-01-01",
            "targetDate": "2024-12-31",
            "color": "#FF0000",
            "lead": {"name": "John Doe"}
        }

        project = Project.from_linear_data(data)
        gantt_dict = project.to_gantt_dict()

        assert gantt_dict["id"] == "project-123"
        assert gantt_dict["name"] == "Test Project"
        assert gantt_dict["start"] == "2024-01-01"
        assert gantt_dict["end"] == "2024-12-31"
        assert gantt_dict["status"] == "in_progress"
        assert gantt_dict["lead"] == "John Doe"


class TestIssue:
    """Tests for Issue model"""

    def test_from_linear_data_basic(self):
        """Test creating Issue from basic Linear data"""
        data = {
            "id": "issue-123",
            "title": "Test Issue"
        }

        issue = Issue.from_linear_data(data)

        assert issue.id == "issue-123"
        assert issue.title == "Test Issue"
        assert issue.priority == 0

    def test_from_linear_data_with_state(self):
        """Test creating Issue with state"""
        data = {
            "id": "issue-123",
            "title": "Test Issue",
            "state": {
                "id": "state-1",
                "name": "In Progress",
                "type": "started",
                "color": "#0000FF"
            }
        }

        issue = Issue.from_linear_data(data)

        assert issue.state is not None
        assert issue.state.name == "In Progress"
        assert issue.state.type == "started"

    def test_from_linear_data_with_assignee(self):
        """Test creating Issue with assignee"""
        data = {
            "id": "issue-123",
            "title": "Test Issue",
            "assignee": {
                "id": "user-1",
                "name": "John Doe",
                "email": "john@example.com"
            }
        }

        issue = Issue.from_linear_data(data)

        assert issue.assignee is not None
        assert issue.assignee.name == "John Doe"
        assert issue.assignee.email == "john@example.com"

    def test_from_linear_data_with_labels(self):
        """Test creating Issue with labels"""
        data = {
            "id": "issue-123",
            "title": "Test Issue",
            "labels": {
                "nodes": [
                    {"id": "label-1", "name": "bug", "color": "#FF0000"},
                    {"id": "label-2", "name": "urgent", "color": "#FFA500"}
                ]
            }
        }

        issue = Issue.from_linear_data(data)

        assert len(issue.labels) == 2
        assert issue.labels[0].name == "bug"
        assert issue.labels[1].name == "urgent"

    def test_get_status_completed(self):
        """Test status for completed issue"""
        data = {
            "id": "issue-123",
            "title": "Test Issue",
            "state": {
                "id": "state-1",
                "name": "Done",
                "type": "completed",
                "color": "#00FF00"
            }
        }

        issue = Issue.from_linear_data(data)
        assert issue.get_status() == "done"

    def test_get_priority_label(self):
        """Test priority label conversion"""
        data = {
            "id": "issue-123",
            "title": "Test Issue",
            "priority": 1
        }

        issue = Issue.from_linear_data(data)
        assert issue.get_priority_label() == "urgent"

    def test_is_overdue(self):
        """Test overdue detection for issues"""
        data = {
            "id": "issue-123",
            "title": "Test Issue",
            "dueDate": "2020-01-01"
        }

        issue = Issue.from_linear_data(data)
        assert issue.is_overdue() is True
