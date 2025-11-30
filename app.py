"""
Linear Gantt Chart Visualizer
Main Streamlit application for visualizing Linear projects as Gantt charts
"""

import streamlit as st
from dotenv import load_dotenv
import os
from datetime import date, timedelta

from src.api.linear_client import LinearClient, LinearAPIError
from src.models.project import Project
from src.models.issue import Issue
from src.visualization.gantt import create_gantt_chart, filter_projects_by_date_range
from src.utils.cache import cached_api_call, clear_cache
from src.utils.auth import validate_api_key

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Linear Gantt Chart",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@cached_api_call()
def fetch_projects_with_issues(_client: LinearClient):
    """
    Fetch all projects and their issues from Linear
    Only includes projects with both start and target dates defined

    Args:
        _client: Linear API client (underscore prefix tells Streamlit not to hash this)

    Returns:
        List of Project objects with valid dates
    """
    # Fetch all projects
    projects_data = _client.get_projects()
    projects = []

    for project_data in projects_data:
        # Skip projects without both start and target dates
        if not project_data.get("startDate") or not project_data.get("targetDate"):
            continue

        # Fetch issues for each project to calculate progress
        try:
            issues_data = _client.get_project_issues(project_data["id"])
            project = Project.from_linear_data(project_data, issues_data)
            projects.append(project)
        except Exception as e:
            st.warning(f"Could not fetch issues for project {project_data['name']}: {str(e)}")
            # Create project without issues
            project = Project.from_linear_data(project_data)
            projects.append(project)

    return projects


def main():
    """Main application entry point"""

    # Header
    st.title("📊 Linear Gantt Chart Visualizer")
    st.markdown("Visualize Linear projects as interactive Gantt charts")

    # Check for API key
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        st.error("⚠️ LINEAR_API_KEY not found. Please set it in your .env file.")
        st.info("Copy .env.example to .env and add your Linear API key")
        st.stop()

    # Validate API key
    with st.spinner("Validating API key..."):
        is_valid, message = validate_api_key(api_key)
        if not is_valid:
            st.error(f"❌ API key validation failed: {message}")
            st.stop()

    # Initialize Linear client
    client = LinearClient()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            clear_cache()
            st.rerun()

        st.divider()

        # Filters
        st.subheader("Filters")

        # Date range filter
        use_date_filter = st.checkbox("Filter by date range", value=False)
        date_start = None
        date_end = None

        if use_date_filter:
            col1, col2 = st.columns(2)
            with col1:
                date_start = st.date_input(
                    "Start date",
                    value=date.today() - timedelta(days=90)
                )
            with col2:
                date_end = st.date_input(
                    "End date",
                    value=date.today() + timedelta(days=90)
                )

        st.divider()

        # Visualization options
        st.subheader("Visualization")

        color_by = st.selectbox(
            "Color by",
            options=["status", "priority"],
            index=0
        )

        show_progress = st.checkbox("Show progress bars", value=True)

        chart_height = st.slider(
            "Chart height",
            min_value=400,
            max_value=1200,
            value=600,
            step=50
        )

    # Main content
    try:
        # Fetch projects
        with st.spinner("Fetching projects from Linear..."):
            projects = fetch_projects_with_issues(client)

        if not projects:
            st.warning("No projects found in your Linear workspace.")
            st.info("Create some projects in Linear to see them visualized here.")
            st.stop()

        # Show stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", len(projects))
        with col2:
            total_issues = sum(p.issue_count for p in projects)
            st.metric("Total Issues", total_issues)
        with col3:
            completed_issues = sum(p.completed_issue_count for p in projects)
            st.metric("Completed Issues", completed_issues)
        with col4:
            avg_progress = sum(p.progress for p in projects) / len(projects) if projects else 0
            st.metric("Avg Progress", f"{avg_progress:.1f}%")

        st.divider()

        # Convert projects to Gantt format
        gantt_data = [p.to_gantt_dict() for p in projects]

        # Apply date filter if enabled
        if use_date_filter and date_start and date_end:
            gantt_data = filter_projects_by_date_range(gantt_data, date_start, date_end)

        if not gantt_data:
            st.warning("No projects match the selected filters.")
        else:
            # Create and display Gantt chart
            fig = create_gantt_chart(
                gantt_data,
                color_by=color_by,
                show_progress=show_progress,
                height=chart_height
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show project details
            with st.expander("📋 Project Details"):
                for project in projects:
                    if use_date_filter:
                        # Check if project is in filtered list
                        if not any(g["id"] == project.id for g in gantt_data):
                            continue

                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        status_emoji = {
                            "done": "✅",
                            "in_progress": "🔄",
                            "todo": "📝",
                            "cancelled": "❌"
                        }
                        emoji = status_emoji.get(project.get_status(), "📝")
                        st.markdown(f"**{emoji} {project.name}**")
                        if project.description:
                            st.caption(project.description[:100] + "..." if len(project.description) > 100 else project.description)
                    with col2:
                        st.metric("Progress", f"{project.progress:.0f}%")
                    with col3:
                        st.metric("Issues", f"{project.completed_issue_count}/{project.issue_count}")

                    if project.is_overdue():
                        st.warning(f"⚠️ Overdue since {project.target_date}")

                    st.divider()

    except LinearAPIError as e:
        st.error(f"❌ Linear API Error: {str(e)}")
        st.info("Please check your API key and internet connection.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
