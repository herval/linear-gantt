"""
Linear API Client
Handles communication with the Linear GraphQL API
"""

import requests
import time
from typing import Optional, List, Dict, Any
from config.settings import (
    LINEAR_API_URL,
    LINEAR_RATE_LIMIT,
    BACKOFF_FACTOR,
    MAX_ISSUES_PER_REQUEST
)
from src.utils.auth import get_auth_headers
from src.api.queries import (
    QUERY_PROJECTS,
    QUERY_PROJECT_ISSUES,
    QUERY_TEAMS,
    QUERY_PROJECTS_WITH_STATS,
    QUERY_PROJECT_DEPENDENCIES,
    QUERY_VIEWER,
    build_paginated_query
)


class LinearAPIError(Exception):
    """Custom exception for Linear API errors"""
    pass


class LinearClient:
    """Client for interacting with the Linear GraphQL API"""

    def __init__(self):
        self.api_url = LINEAR_API_URL
        self.headers = get_auth_headers()
        self.request_count = 0
        self.last_request_time = time.time()

    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """
        Execute a GraphQL query with rate limiting and error handling

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            dict: Query response data

        Raises:
            LinearAPIError: If the API request fails
        """
        # Simple rate limiting check
        self._check_rate_limit()

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            self.request_count += 1
            self.last_request_time = time.time()

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    error_messages = [e.get("message", "Unknown error") for e in data["errors"]]
                    raise LinearAPIError(f"GraphQL errors: {', '.join(error_messages)}")
                return data.get("data", {})
            elif response.status_code == 429:
                # Rate limited - implement exponential backoff
                retry_after = int(response.headers.get("Retry-After", 60))
                raise LinearAPIError(f"Rate limited. Retry after {retry_after} seconds")
            else:
                raise LinearAPIError(f"API request failed with status {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise LinearAPIError(f"Request failed: {str(e)}")

    def _check_rate_limit(self):
        """Simple rate limiting check"""
        # Reset counter every hour
        if time.time() - self.last_request_time > 3600:
            self.request_count = 0

        if self.request_count >= LINEAR_RATE_LIMIT:
            raise LinearAPIError("Rate limit reached. Please wait before making more requests")

    def _fetch_paginated(self, query: str, variables: Optional[Dict] = None,
                        data_key: str = "projects") -> List[Dict]:
        """
        Fetch all pages of a paginated query

        Args:
            query: GraphQL query
            variables: Query variables
            data_key: Key in response containing the paginated data

        Returns:
            list: All fetched items
        """
        all_items = []
        has_next_page = True
        after = None
        vars_dict = variables or {}

        while has_next_page:
            if after:
                vars_dict["after"] = after

            data = self._execute_query(query, vars_dict)

            if data_key in data:
                page_data = data[data_key]
                all_items.extend(page_data.get("nodes", []))

                page_info = page_data.get("pageInfo", {})
                has_next_page = page_info.get("hasNextPage", False)
                after = page_info.get("endCursor")
            else:
                has_next_page = False

        return all_items

    def get_viewer(self) -> Optional[Dict]:
        """
        Get current viewer (authenticated user) information

        Returns:
            dict: Viewer information
        """
        try:
            data = self._execute_query(QUERY_VIEWER)
            return data.get("viewer")
        except LinearAPIError:
            return None

    def get_teams(self) -> List[Dict]:
        """
        Fetch all teams

        Returns:
            list: List of teams
        """
        data = self._execute_query(QUERY_TEAMS)
        return data.get("teams", {}).get("nodes", [])

    def get_projects(self, include_stats: bool = False) -> List[Dict]:
        """
        Fetch all projects

        Args:
            include_stats: Whether to include issue statistics

        Returns:
            list: List of projects
        """
        query = QUERY_PROJECTS_WITH_STATS if include_stats else QUERY_PROJECTS
        return self._fetch_paginated(query, data_key="projects")

    def get_project_issues(self, project_id: str) -> List[Dict]:
        """
        Fetch all issues for a specific project

        Args:
            project_id: Linear project ID

        Returns:
            list: List of issues
        """
        variables = {"projectId": project_id}
        data = self._execute_query(QUERY_PROJECT_ISSUES, variables)

        project_data = data.get("project", {})
        issues_data = project_data.get("issues", {})

        # Handle pagination if needed
        all_issues = issues_data.get("nodes", [])
        page_info = issues_data.get("pageInfo", {})

        while page_info.get("hasNextPage"):
            variables["after"] = page_info.get("endCursor")
            data = self._execute_query(QUERY_PROJECT_ISSUES, variables)
            project_data = data.get("project", {})
            issues_data = project_data.get("issues", {})
            all_issues.extend(issues_data.get("nodes", []))
            page_info = issues_data.get("pageInfo", {})

        return all_issues

    def get_project_dependencies(self, project_id: str) -> List[Dict]:
        """
        Fetch dependency relationships for a project

        Args:
            project_id: Linear project ID

        Returns:
            list: List of issues with their relations
        """
        variables = {"projectId": project_id}
        data = self._execute_query(QUERY_PROJECT_DEPENDENCIES, variables)

        project_data = data.get("project", {})
        issues_data = project_data.get("issues", {})

        return issues_data.get("nodes", [])
