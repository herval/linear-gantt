"""
Project data model for Linear projects
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, date


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
            completed_issue_count=completed_issue_count
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

    def to_gantt_dict(self) -> dict:
        """
        Convert to dictionary format suitable for Gantt chart rendering

        Returns:
            dict: Gantt chart data
        """
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start_date.isoformat() if self.start_date else None,
            "end": self.target_date.isoformat() if self.target_date else None,
            "progress": self.progress,
            "status": self.get_status(),
            "color": self.color,
            "lead": self.lead_name,
            "is_overdue": self.is_overdue(),
            "issue_count": self.issue_count,
            "completed_issues": self.completed_issue_count
        }
