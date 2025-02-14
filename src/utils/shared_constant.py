
from enum import Enum

class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class GoalCategory(Enum):
    HABIT = "Habit"
    PROJECT = "Project"

class GoalStatus(Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    INACTIVE = "Inactive"

