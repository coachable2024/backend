from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class HabitStatus(str, Enum):
    ACTIVE = "Active"  # Changed to match incoming data
    PAUSED = "Paused"
    ARCHIVED = "Archived"

class HabitFrequency(str, Enum):
    DAILY = "Daily"    # Changed to match incoming data
    WEEKLY = "Weekly"

class HabitSchedule(BaseModel):
    frequency: HabitFrequency
    preferred_time: Optional[str] = Field(default=None, alias="preferredTime")
    duration: Optional[int] = None
    
    class Config:
        populate_by_name = True

class Habit(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    category: Optional[str] = None
    frequency: Optional[str] = None
    preferred_time: Optional[str] = Field(default=None, alias="preferredTime")
    duration: Optional[int] = 0
    completed_dates: Optional[List[datetime]] = Field(default=None, alias="completedDates")
    status: Optional[HabitStatus] = Field(default=HabitStatus.ACTIVE)
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, alias="updatedAt")

    class Config:
        populate_by_name = True

class Task(BaseModel):
    id: Optional[str] = None
    category: Optional[str] = None
    title: str
    description: str
    frequency: Optional[str] = None
    preferred_time: Optional[str] = Field(default=None, alias="preferredTime")
    duration: Optional[int] = None
    completed_date: Optional[datetime] = Field(default=None, alias="completedDate")
    status: str
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")

    class Config:
        populate_by_name = True

class Goal(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[str] = Field(default=None, alias="targetDate")  # Keep as string
    hours_dedicated: Optional[int] = Field(default=None, alias="hoursDedicated")
    confirm_goal: Optional[bool] = None
    add_habits: Optional[bool] = None
    habits: List[Habit] = Field(default_factory=list)
    confirm_habit: Optional[bool] = None
    tasks: List[Task] = Field(default_factory=list)
    confirm_tasks: Optional[bool] = None
    status: Optional[str] = None
    created_at: Optional[str] = Field(default=None, alias="createdAt")  # Keep as string
    completed_date: Optional[str] = Field(default=None, alias="completedDate")
    clear_chat: Optional[bool] = None

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        # Convert datetime objects to strings in the format you want
        if isinstance(d.get('target_date'), datetime):
            d['target_date'] = d['target_date'].strftime('%Y-%m-%d')
        if isinstance(d.get('created_at'), datetime):
            d['created_at'] = d['created_at'].strftime('%Y-%m-%d')
        if isinstance(d.get('completed_date'), datetime):
            d['completed_date'] = d['completed_date'].strftime('%Y-%m-%d')
        return d

class WorkFlowManager(BaseModel):
    goal: Goal = Field(default_factory=Goal)
    chat_history: List[Dict[str, str]] = Field(default_factory=list)

    class Config:
        populate_by_name = True