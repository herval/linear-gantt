"""
Project data model for Linear projects
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, date, timedelta


@dataclass
class Project:
    """Represents a Linear project with Gantt chart relevant data"""

    id: str
    name: str
    state: str
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    lead_id: Optional[str] = None
    lead_name: Optional[str] = None
    member_ids: List[str] = field(default_factory=list)
    issue_count: int = 0
    completed_issue_count: int = 0
    dependencies: List[str] = field(default_factory=list)  # Project IDs this blocks
    blocked_by: List[str] = field(default_factory=list)  # Project IDs blocking this
    _issues_data: List[dict] = field(default_factory=list, repr=False)  # Raw issues data for calculations

    @classmethod
    def from_linear_data(cls, data: dict, issues: Optional[List] = None) -> 'Project':
        """
        Create Project instance from Linear API data

        Args:
            data: Raw project data from Linear API
            issues: Optional list of issues to calculate progress

        Returns:
            Project: Project instance
        """
        # Parse dates
        start_date = None
        if data.get("startDate"):
            try:
                start_date = datetime.fromisoformat(data["startDate"]).date()
            except (ValueError, TypeError):
                pass

        target_date = None
        if data.get("targetDate"):
            try:
                target_date = datetime.fromisoformat(data["targetDate"]).date()
            except (ValueError, TypeError):
                pass

        completed_at = None
        if data.get("completedAt"):
            try:
                completed_at = datetime.fromisoformat(data["completedAt"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # Extract lead info
        lead = data.get("lead", {})
        lead_id = lead.get("id") if lead else None
        lead_name = lead.get("name") if lead else None

        # Extract member IDs
        members = data.get("members", {}).get("nodes", [])
        member_ids = [m["id"] for m in members if "id" in m]

        # Calculate progress from issues if provided
        progress = data.get("progress", 0.0)
        issue_count = 0
        completed_issue_count = 0

        if issues:
            issue_count = len(issues)
            completed_issue_count = sum(1 for issue in issues
                                      if issue.get("state", {}).get("type") == "completed")
            if issue_count > 0:
                progress = (completed_issue_count / issue_count) * 100

        return cls(
            id=data["id"],
            name=data["name"],
            state=data.get("state", "planned"),
            start_date=start_date,
            target_date=target_date,
            completed_at=completed_at,
            progress=round(progress, 2),
            description=data.get("description"),
            color=data.get("color"),
            icon=data.get("icon"),
            lead_id=lead_id,
            lead_name=lead_name,
            member_ids=member_ids,
            issue_count=issue_count,
            completed_issue_count=completed_issue_count,
            _issues_data=issues or []
        )

    def get_status(self) -> str:
        """
        Get normalized status for color coding

        Returns:
            str: Status (todo, in_progress, done, cancelled)
        """
        state_lower = self.state.lower()

        if self.completed_at or state_lower in ["completed", "done"]:
            return "done"
        elif state_lower in ["cancelled", "canceled"]:
            return "cancelled"
        elif state_lower in ["started", "in progress", "active"]:
            return "in_progress"
        else:
            return "todo"

    def get_duration_days(self) -> Optional[int]:
        """
        Calculate project duration in days

        Returns:
            int: Duration in days or None if dates not set
        """
        if self.start_date and self.target_date:
            return (self.target_date - self.start_date).days
        return None

    def is_overdue(self) -> bool:
        """
        Check if project is overdue

        Returns:
            bool: True if overdue
        """
        if self.target_date and not self.completed_at:
            return date.today() > self.target_date
        return False

    def get_effective_start_date(self) -> Optional[date]:
        """
        Calculate effective start date based on project state and issues

        Logic:
        - For "Planned" projects: use project start date
        - For "In Progress" projects: use date of oldest ticket that's done or in progress
        - If no valid date found, return None

        Returns:
            date: Effective start date or None
        """
        state_lower = self.state.lower()

        # For planned projects, use the project start date
        if state_lower in ["planned", "todo"]:
            return self.start_date

        # For in-progress projects, find oldest started/completed issue
        if state_lower in ["started", "in progress", "active"]:
            oldest_date = None

            for issue in self._issues_data:
                # Check if issue is done or in progress
                state_type = issue.get("state", {}).get("type", "").lower()
                if state_type not in ["started", "completed"]:
                    continue

                # Get the relevant date (startedAt or completedAt)
                issue_date = None
                if issue.get("startedAt"):
                    try:
                        issue_date = datetime.fromisoformat(issue["startedAt"].replace("Z", "+00:00")).date()
                    except (ValueError, TypeError):
                        pass

                if not issue_date and issue.get("completedAt"):
                    try:
                        issue_date = datetime.fromisoformat(issue["completedAt"].replace("Z", "+00:00")).date()
                    except (ValueError, TypeError):
                        pass

                # Track the oldest date
                if issue_date:
                    if oldest_date is None or issue_date < oldest_date:
                        oldest_date = issue_date

            # Return oldest issue date if found, otherwise fall back to project start date
            return oldest_date if oldest_date else self.start_date

        # For other states, use project start date
        return self.start_date

    def get_effective_end_date(self) -> Optional[date]:
        """
        Calculate effective end date

        Logic:
        - If project has a target date, use it
        - Otherwise, use effective start date + 6 months
        - If no start date available, return None

        Returns:
            date: Effective end date or None
        """
        # If target date is set, use it
        if self.target_date:
            return self.target_date

        # Otherwise, calculate from effective start date
        start = self.get_effective_start_date()
        if start:
            # Add 6 months (approximately 180 days)
            return start + timedelta(days=180)

        return None

    def to_gantt_dict(self) -> dict:
        """
        Convert to dictionary format suitable for Gantt chart rendering
        Uses effective dates calculated based on project state and issues

        Returns:
            dict: Gantt chart data
        """
        effective_start = self.get_effective_start_date()
        effective_end = self.get_effective_end_date()

        return {
            "id": self.id,
            "name": self.name,
            "start": effective_start.isoformat() if effective_start else None,
            "end": effective_end.isoformat() if effective_end else None,
            "progress": self.progress,
            "status": self.get_status(),
            "color": self.color,
            "lead": self.lead_name,
            "is_overdue": self.is_overdue(),
            "issue_count": self.issue_count,
            "completed_issues": self.completed_issue_count
        }
