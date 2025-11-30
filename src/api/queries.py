"""
GraphQL queries for Linear API
"""

# Query to fetch all projects with their details
QUERY_PROJECTS = """
query Projects($after: String) {
    projects(first: 50, after: $after) {
        pageInfo {
            hasNextPage
            endCursor
        }
        nodes {
            id
            name
            description
            state
            startDate
            targetDate
            completedAt
            progress
            color
            icon
            lead {
                id
                name
                email
            }
            members {
                nodes {
                    id
                    name
                }
            }
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
    }
}
"""

# Query to fetch issues for a specific project
QUERY_PROJECT_ISSUES = """
query ProjectIssues($projectId: String!, $after: String) {
    project(id: $projectId) {
        id
        name
        issues(first: 100, after: $after) {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                id
                title
                description
                priority
                estimate
                startedAt
                dueDate
                completedAt
                createdAt
                state {
                    id
                    name
                    type
                    color
                }
                assignee {
                    id
                    name
                    email
                    avatarUrl
                }
                labels {
                    nodes {
                        id
                        name
                        color
                    }
                }
                parent {
                    id
                    title
                }
                cycle {
                    id
                    name
                    startsAt
                    endsAt
                }
                relations {
                    nodes {
                        type
                        relatedIssue {
                            id
                            title
                            project {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
}
"""

# Query to fetch teams (needed for team-based queries)
QUERY_TEAMS = """
query Teams {
    teams {
        nodes {
            id
            name
            key
            description
        }
    }
}
"""

# Query to fetch all projects with basic issue stats for calculating progress
QUERY_PROJECTS_WITH_STATS = """
query ProjectsWithStats($after: String) {
    projects(first: 50, after: $after) {
        pageInfo {
            hasNextPage
            endCursor
        }
        nodes {
            id
            name
            description
            state
            startDate
            targetDate
            completedAt
            progress
            color
            icon
            issueCountHistory {
                date
                total
                completed
            }
            lead {
                id
                name
            }
        }
    }
}
"""

# Query to fetch project dependencies (issues that block/are blocked by)
QUERY_PROJECT_DEPENDENCIES = """
query ProjectDependencies($projectId: String!, $after: String) {
    project(id: $projectId) {
        id
        issues(first: 100, after: $after) {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                id
                relations {
                    nodes {
                        type
                        relatedIssue {
                            id
                            title
                            project {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
}
"""

# Query to get viewer (current user) information
QUERY_VIEWER = """
query Viewer {
    viewer {
        id
        name
        email
        admin
        organization {
            id
            name
        }
    }
}
"""


def build_paginated_query(base_query: str, variables: dict, after: str = None) -> dict:
    """
    Build a paginated query with cursor

    Args:
        base_query: The base GraphQL query
        variables: Query variables
        after: Cursor for pagination

    Returns:
        dict: Query payload
    """
    if after:
        variables["after"] = after

    return {
        "query": base_query,
        "variables": variables
    }
