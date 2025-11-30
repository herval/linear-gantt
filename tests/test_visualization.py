"""
Tests for Gantt chart visualization
"""

import pytest
from datetime import date, timedelta
from src.visualization.gantt import (
    create_gantt_chart,
    filter_projects_by_date_range,
    group_projects
)


class TestGanttChart:
    """Tests for Gantt chart creation"""

    def test_create_gantt_chart_empty(self):
        """Test creating Gantt chart with empty data"""
        fig = create_gantt_chart([])

        assert fig is not None
        # Should create a figure with a message

    def test_create_gantt_chart_with_projects(self):
        """Test creating Gantt chart with valid projects"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": "2024-01-01",
                "end": "2024-03-31",
                "progress": 50.0,
                "status": "in_progress",
                "issue_count": 10,
                "completed_issues": 5
            },
            {
                "id": "project-2",
                "name": "Project 2",
                "start": "2024-02-01",
                "end": "2024-04-30",
                "progress": 25.0,
                "status": "todo",
                "issue_count": 8,
                "completed_issues": 2
            }
        ]

        fig = create_gantt_chart(projects, color_by="status", show_progress=True)

        assert fig is not None
        assert len(fig.data) > 0  # Should have traces

    def test_create_gantt_chart_without_dates(self):
        """Test creating Gantt chart with projects missing dates"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": None,
                "end": None,
                "progress": 0.0,
                "status": "todo"
            }
        ]

        fig = create_gantt_chart(projects)

        assert fig is not None
        # Should handle missing dates gracefully

    def test_create_gantt_chart_color_by_priority(self):
        """Test creating Gantt chart colored by priority"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": "2024-01-01",
                "end": "2024-03-31",
                "progress": 50.0,
                "status": "in_progress",
                "priority": "high",
                "issue_count": 10,
                "completed_issues": 5
            }
        ]

        fig = create_gantt_chart(projects, color_by="priority")

        assert fig is not None

    def test_create_gantt_chart_custom_height(self):
        """Test creating Gantt chart with custom height"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": "2024-01-01",
                "end": "2024-03-31",
                "progress": 50.0,
                "status": "in_progress",
                "issue_count": 10,
                "completed_issues": 5
            }
        ]

        fig = create_gantt_chart(projects, height=800)

        assert fig is not None
        assert fig.layout.height == 800


class TestFilterProjects:
    """Tests for project filtering"""

    def test_filter_projects_no_filters(self):
        """Test filtering with no date range"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": "2024-01-01",
                "end": "2024-03-31"
            }
        ]

        filtered = filter_projects_by_date_range(projects)

        assert len(filtered) == 1

    def test_filter_projects_by_start_date(self):
        """Test filtering by start date"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": "2024-01-01",
                "end": "2024-03-31"
            },
            {
                "id": "project-2",
                "name": "Project 2",
                "start": "2024-06-01",
                "end": "2024-08-31"
            }
        ]

        filtered = filter_projects_by_date_range(
            projects,
            start_date=date(2024, 5, 1)
        )

        assert len(filtered) == 1
        assert filtered[0]["id"] == "project-2"

    def test_filter_projects_by_end_date(self):
        """Test filtering by end date"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": "2024-01-01",
                "end": "2024-03-31"
            },
            {
                "id": "project-2",
                "name": "Project 2",
                "start": "2024-06-01",
                "end": "2024-08-31"
            }
        ]

        filtered = filter_projects_by_date_range(
            projects,
            end_date=date(2024, 5, 1)
        )

        assert len(filtered) == 1
        assert filtered[0]["id"] == "project-1"

    def test_filter_projects_by_date_range(self):
        """Test filtering by complete date range"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": "2024-01-01",
                "end": "2024-03-31"
            },
            {
                "id": "project-2",
                "name": "Project 2",
                "start": "2024-02-01",
                "end": "2024-04-30"
            },
            {
                "id": "project-3",
                "name": "Project 3",
                "start": "2024-06-01",
                "end": "2024-08-31"
            }
        ]

        filtered = filter_projects_by_date_range(
            projects,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 5, 15)
        )

        assert len(filtered) == 2
        assert filtered[0]["id"] == "project-1"
        assert filtered[1]["id"] == "project-2"

    def test_filter_projects_missing_dates(self):
        """Test filtering projects with missing dates"""
        projects = [
            {
                "id": "project-1",
                "name": "Project 1",
                "start": None,
                "end": None
            },
            {
                "id": "project-2",
                "name": "Project 2",
                "start": "2024-01-01",
                "end": "2024-03-31"
            }
        ]

        filtered = filter_projects_by_date_range(
            projects,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )

        # Only project with valid dates should be included
        assert len(filtered) == 1
        assert filtered[0]["id"] == "project-2"


class TestGroupProjects:
    """Tests for project grouping"""

    def test_group_projects_by_status(self):
        """Test grouping projects by status"""
        projects = [
            {"id": "1", "name": "P1", "status": "in_progress"},
            {"id": "2", "name": "P2", "status": "todo"},
            {"id": "3", "name": "P3", "status": "in_progress"}
        ]

        grouped = group_projects(projects, "status")

        assert len(grouped) == 2
        assert len(grouped["in_progress"]) == 2
        assert len(grouped["todo"]) == 1

    def test_group_projects_by_lead(self):
        """Test grouping projects by lead"""
        projects = [
            {"id": "1", "name": "P1", "lead": "Alice"},
            {"id": "2", "name": "P2", "lead": "Bob"},
            {"id": "3", "name": "P3", "lead": "Alice"}
        ]

        grouped = group_projects(projects, "lead")

        assert len(grouped) == 2
        assert len(grouped["Alice"]) == 2
        assert len(grouped["Bob"]) == 1

    def test_group_projects_with_unknown(self):
        """Test grouping projects with missing fields"""
        projects = [
            {"id": "1", "name": "P1", "status": "todo"},
            {"id": "2", "name": "P2"}  # Missing status
        ]

        grouped = group_projects(projects, "status")

        assert "todo" in grouped
        assert "Unknown" in grouped
        assert len(grouped["Unknown"]) == 1
