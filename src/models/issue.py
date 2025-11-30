"""
Issue data model for Linear issues
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, date


@dataclass
class IssueLabel:
    """Represents a Linear issue label"""
    id: str
    name: str
    color: str


@dataclass
class IssueState:
    """Represents a Linear issue state"""
    id: str
    name: str
    type: str  # backlog, unstarted, started, completed, canceled
    color: str


@dataclass
class Assignee:
    """Represents an issue assignee"""
    id: str
    name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class Cycle:
    """Represents a Linear cycle/sprint"""
    id: str
    name: str
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


@dataclass
class Issue:
    """Represents a Linear issue"""

    id: str
    title: str
    project_id: Optional[str] = None
    priority: int = 0  # 0 = None, 1 = Urgent, 2 = High, 3 = Medium, 4 = Low
    estimate: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    state: Optional[IssueState] = None
    assignee: Optional[Assignee] = None
    labels: List[IssueLabel] = field(default_factory=list)
    parent_id: Optional[str] = None
    cycle: Optional[Cycle] = None
    relations: List[dict] = field(default_factory=list)

    @classmethod
    def from_linear_data(cls, data: dict) -> 'Issue':
        """
        Create Issue instance from Linear API data

        Args:
            data: Raw issue data from Linear API

        Returns:
            Issue: Issue instance
        """
        # Parse dates
        created_at = None
        if data.get("createdAt"):
            try:
                created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        started_at = None
        if data.get("startedAt"):
            try:
                started_at = datetime.fromisoformat(data["startedAt"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        due_date = None
        if data.get("dueDate"):
            try:
                due_date = datetime.fromisoformat(data["dueDate"]).date()
            except (ValueError, TypeError):
                pass

        completed_at = None
        if data.get("completedAt"):
            try:
                completed_at = datetime.fromisoformat(data["completedAt"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # Parse state
        state = None
        if data.get("state"):
            state_data = data["state"]
            state = IssueState(
                id=state_data.get("id", ""),
                name=state_data.get("name", ""),
                type=state_data.get("type", ""),
                color=state_data.get("color", "")
            )

        # Parse assignee
        assignee = None
        if data.get("assignee"):
            assignee_data = data["assignee"]
            assignee = Assignee(
                id=assignee_data.get("id", ""),
                name=assignee_data.get("name", ""),
                email=assignee_data.get("email"),
                avatar_url=assignee_data.get("avatarUrl")
            )

        # Parse labels
        labels = []
        if data.get("labels", {}).get("nodes"):
            for label_data in data["labels"]["nodes"]:
                labels.append(IssueLabel(
                    id=label_data.get("id", ""),
                    name=label_data.get("name", ""),
                    color=label_data.get("color", "")
                ))

        # Parse cycle
        cycle = None
        if data.get("cycle"):
            cycle_data = data["cycle"]
            starts_at = None
            ends_at = None

            if cycle_data.get("startsAt"):
                try:
                    starts_at = datetime.fromisoformat(cycle_data["startsAt"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            if cycle_data.get("endsAt"):
                try:
                    ends_at = datetime.fromisoformat(cycle_data["endsAt"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            cycle = Cycle(
                id=cycle_data.get("id", ""),
                name=cycle_data.get("name", ""),
                starts_at=starts_at,
                ends_at=ends_at
            )

        # Get parent ID
        parent_id = None
        if data.get("parent"):
            parent_id = data["parent"].get("id")

        # Get relations
        relations = []
        if data.get("relations", {}).get("nodes"):
            relations = data["relations"]["nodes"]

        return cls(
            id=data["id"],
            title=data["title"],
            priority=data.get("priority", 0),
            estimate=data.get("estimate"),
            description=data.get("description"),
            created_at=created_at,
            started_at=started_at,
            due_date=due_date,
            completed_at=completed_at,
            state=state,
            assignee=assignee,
            labels=labels,
            parent_id=parent_id,
            cycle=cycle,
            relations=relations
        )

    def get_status(self) -> str:
        """
        Get normalized status for color coding

        Returns:
            str: Status (todo, in_progress, done, cancelled)
        """
        if not self.state:
            return "todo"

        state_type = self.state.type.lower()
        if state_type in ["completed", "done"]:
            return "done"
        elif state_type in ["canceled", "cancelled"]:
            return "cancelled"
        elif state_type in ["started"]:
            return "in_progress"
        else:
            return "todo"

    def get_priority_label(self) -> str:
        """
        Get priority as string

        Returns:
            str: Priority label
        """
        priority_map = {
            0: "none",
            1: "urgent",
            2: "high",
            3: "medium",
            4: "low"
        }
        return priority_map.get(self.priority, "none")

    def is_overdue(self) -> bool:
        """
        Check if issue is overdue

        Returns:
            bool: True if overdue
        """
        if self.due_date and not self.completed_at:
            return date.today() > self.due_date
        return False
