"""
Gantt chart visualization using Plotly
"""

import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from config.settings import STATUS_COLORS, PRIORITY_COLORS


def create_gantt_chart(projects: List[Dict],
                       color_by: str = "status",
                       show_progress: bool = True,
                       height: int = 600) -> go.Figure:
    """
    Create a Gantt chart from project data

    Args:
        projects: List of project dictionaries (from Project.to_gantt_dict())
        color_by: Color coding method ("status" or "priority")
        show_progress: Whether to show progress bars
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    if not projects:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No projects to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(height=height)
        return fig

    # Prepare data for Gantt chart using Plotly timeline
    tasks = []
    today = date.today()

    for project in projects:
        # Skip projects without dates
        if not project.get("start") or not project.get("end"):
            print(f"Skipping project {project.get('name')} - missing dates")
            continue

        # Determine color
        if color_by == "status":
            color = STATUS_COLORS.get(project.get("status", "todo"), STATUS_COLORS["todo"])
        else:
            color = PRIORITY_COLORS.get(project.get("priority", "medium"), PRIORITY_COLORS["medium"])

        # Create task entry for plotly timeline
        task = dict(
            Task=project["name"],
            Start=project["start"],
            Finish=project["end"],
            Resource=project.get("status", "todo"),
            Description=f"{project.get('issue_count', 0)} issues ({project.get('completed_issues', 0)} completed)",
            Progress=project.get("progress", 0),
            Color=color
        )
        tasks.append(task)
        print(f"Added task: {project['name']} from {project['start']} to {project['end']}")

    if not tasks:
        # No valid projects with dates
        fig = go.Figure()
        fig.add_annotation(
            text="No projects with valid dates to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(height=height)
        return fig

    print(f"Creating Gantt chart with {len(tasks)} tasks")

    # Create figure using timeline approach
    fig = go.Figure()

    # Sort tasks by start date
    tasks_sorted = sorted(tasks, key=lambda x: x['Start'])

    # Add bars for each project
    for task in tasks_sorted:
        # Parse dates as strings (Plotly will handle them)
        start_str = task['Start']
        finish_str = task['Finish']
        progress = task.get('Progress', 0)

        print(f"Adding bar for {task['Task']}: {start_str} to {finish_str}")

        # Add background bar (full duration) using Scatter to ensure visibility
        fig.add_trace(go.Scatter(
            x=[start_str, finish_str],
            y=[task['Task'], task['Task']],
            mode='lines',
            line=dict(
                color=task['Color'],
                width=20
            ),
            opacity=0.3,
            showlegend=False,
            hovertemplate=f"<b>{task['Task']}</b><br>" +
                         f"Start: {start_str}<br>" +
                         f"End: {finish_str}<br>" +
                         f"Progress: {progress:.1f}%<br>" +
                         f"{task['Description']}<br>" +
                         "<extra></extra>",
            name=task['Task']
        ))

        # Add progress overlay if there's progress
        if show_progress and progress > 0:
            # Calculate progress end date
            start_date = pd.to_datetime(start_str)
            finish_date = pd.to_datetime(finish_str)
            total_duration = (finish_date - start_date).total_seconds()
            completed_duration = total_duration * (progress / 100)
            completed_end = start_date + timedelta(seconds=completed_duration)

            fig.add_trace(go.Scatter(
                x=[start_str, completed_end.isoformat()],
                y=[task['Task'], task['Task']],
                mode='lines',
                line=dict(
                    color=task['Color'],
                    width=20
                ),
                opacity=1.0,
                showlegend=False,
                hoverinfo='skip',
                name=f"{task['Task']} Progress"
            ))

    # Update layout
    fig.update_layout(
        title="Project Timeline",
        xaxis=dict(
            title="Timeline",
            type='date',
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title="Projects",
            autorange="reversed",  # Show first project at top
        ),
        barmode='overlay',
        height=height,
        hovermode='closest',
        plot_bgcolor='white',
        margin=dict(l=150, r=50, t=80, b=50)
    )

    # Add today line as a shape
    today_str = today.isoformat()
    fig.add_shape(
        type="line",
        x0=today_str,
        x1=today_str,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="red", width=2, dash="dash")
    )

    # Add today annotation
    fig.add_annotation(
        x=today_str,
        y=1,
        yref="paper",
        text="Today",
        showarrow=False,
        yshift=10
    )

    return fig


def filter_projects_by_date_range(projects: List[Dict],
                                  start_date: Optional[date] = None,
                                  end_date: Optional[date] = None) -> List[Dict]:
    """
    Filter projects by date range

    Args:
        projects: List of project dictionaries
        start_date: Filter start date
        end_date: Filter end date

    Returns:
        Filtered list of projects
    """
    if not start_date and not end_date:
        return projects

    filtered = []
    for project in projects:
        project_start = project.get("start")
        project_end = project.get("end")

        if not project_start or not project_end:
            continue

        # Convert string dates to date objects if needed
        if isinstance(project_start, str):
            project_start = datetime.fromisoformat(project_start).date()
        if isinstance(project_end, str):
            project_end = datetime.fromisoformat(project_end).date()

        # Check if project overlaps with date range
        if start_date and project_end < start_date:
            continue
        if end_date and project_start > end_date:
            continue

        filtered.append(project)

    return filtered


def group_projects(projects: List[Dict], group_by: str) -> Dict[str, List[Dict]]:
    """
    Group projects by a specific field

    Args:
        projects: List of project dictionaries
        group_by: Field to group by (status, lead, etc.)

    Returns:
        Dictionary of grouped projects
    """
    groups = {}

    for project in projects:
        key = project.get(group_by, "Unknown")
        if key not in groups:
            groups[key] = []
        groups[key].append(project)

    return groups
