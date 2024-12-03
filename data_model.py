from typing import List, Literal
from pydantic import BaseModel, Field

class HistoryRecord(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    user_input: str
    coach_name: str
    history: List[HistoryRecord] = Field(default_factory=list)

class AnswerWithHistory(BaseModel):
    answer: str
    history: List[HistoryRecord]

class Task(BaseModel):
    id: str = Field(description="The id of the task")
    title: str = Field(description="The title of the task")
    description: str = Field(description="The description of the task")
    status: Literal["Not Started", "In Progress", "Completed"] = Field(description="The status of the task")
    updated_at: str = Field(description="The date the task was last updated")
    created_at: str = Field(description="The date the task was created")
    priority: str = Field(description="The priority of the task")
    due_date: str = Field(description="The due date of the task")
    start_date_time: str = Field(description="The start date time of the task")
    end_date_time: str = Field(description="The end date time of the task")
    duration: str = Field(description="The interval of the task")

class Goal(BaseModel):
    id: str = Field(description="The id of the goal")
    title: str = Field(description="The title of the goal")
    tasks: List[Task] = Field(description="The tasks associated with the goal")
    motivation: str = Field(description="The motivation of the goal")
    status: Literal["Active", "Completed", "Inactive"] = Field(description="The status of the goal")
    category: Literal["Habit", "Project"] = Field(description="The category of the goal")
    user_id: str = Field(description="The user id of the goal")
    description: str = Field(description="The description of the goal")
    created_at: str = Field(description="The start date of the goal")
    completed_date: str = Field(description="The end date of the goal")
    target_date: str = Field(description="The target date of the goal")
    updated_at: str = Field(description="The end date of the goal")
    reward: str = Field(description="The reward of the goal")
    progress: float = Field(description="The progress of the goal")
    confirmed: bool = Field(description="Whether the goal is confirmed")