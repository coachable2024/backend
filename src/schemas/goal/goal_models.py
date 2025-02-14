
from src.utils.shared_constant import GoalStatus
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Task(BaseModel):
  id: Optional[str] = Field(default=None, description="The id of the task")
  category: Literal["Goal_Related_Task"] = Field(description="This is a goal related task")
  title: Optional[str] = Field(default=None, description="The title of the task")
  description: Optional[str] = Field(default=None, description="The description of the task")
  frequency : Optional[str] = Field(default='Daily', description="The frequency of the habit")
  preferred_time : Optional[str] = Field(default=None, description="The preferred time to do this task daily, the format should be '%H:%M'")
  duration: Optional[int] = Field(default=None, le = 24, ge = 0, description="The duration of this task, the unit is hour. ")
  completed_date: Optional[str] = Field(default=None, description="The dates that users complete this task.")
  status: Optional[str] = Field(default='Active', description="The status of the task, can be active or inactive")
  start_date:Optional[str] = Field(default=None, description="The start date of the task")
  end_date:  Optional[str] = Field(default=None, description="The end date of the task")


class Habit(BaseModel):
  id: Optional[str] = Field(default=None, description="The id of the habit")
  category: Literal["Habit"] = Field(description="This is a habit")
  title: Optional[str] = Field(default=None, description="The title of the habit")
  description: Optional[str] = Field(default=None, description="The description of the habit")
  frequency : Optional[str] = Field(default='Daily', description="The frequency of the habit")
  preferred_time : Optional[str] = Field(default=None, description="The preferred time to do this habit daily, the format should be '%H:%M'")
  duration: Optional[int] = Field(default=None, description="The duration of this task, the unit is hour.")
  completed_dates: Optional[str] = Field(default=None, description="The dates that users complete this habit.")
#   scheduled_dates: Optional[str] = Field(default=None, description="The title of the habit")
  status: Optional[str] = Field(default='Active', description="The status of the habit")
#   created_at: Optional[str] = Field(default=None, description="The title of the habit")
#   updated_at: Optional[str] = Field(default=None, description="The title of the habit")
  start_date:Optional[str] = Field(default=None, description="The start date of the habit")
  end_date:  Optional[str] = Field(default=None, description="The end date of the habit")


class Goal(BaseModel):
    id: Optional[str] = Field(default=None, description="The id of the goal")
    user_id: Optional[str] = Field(default=None, description="The user id of the user who set the goal")
    # category: GoalCategory = Field(description="The category of the goal")
    title: Optional[str] = Field(default=None, description="The title of the goal")
    description: Optional[str] = Field(default=None, description="The description of the goal")
    # reward: Optional[str] = Field(default=None, description="The reward of the goal")
    # motivation: Optional[str] = Field(default=None, description="The motivation of the goal")
    target_date: Optional[str] = Field(default=None, description="The target date of the goal")
    hours_dedicated: Optional[int] = Field(default=None, description="How many hours a day dedicated to the goal")
    confirm_goal: Optional[bool] = Field(default=None, description="Whether the goal is confirmed by user.")
    add_habits: Optional[bool] = Field(default=None, description="Whether the user wants to add habits")
    # temp_habit: Habit = Field(default=Habit(), description="Whether the user wants to add habits")
    habits: Optional[List[Habit]] = Field(default=[], description="The habits or daily schedules user has")
    confirm_habit: Optional[bool] = Field(default=None, description="Whether the habits are confirmed")
    tasks: Optional[List[Task]] = Field(default=[], description="The tasks associated with the goal")
    confirm_tasks: Optional[bool] = Field(default=None, description="Whether the tasks are confirmed by user")

    # the rest will be tagged by user or constant
    status: Optional[str] = Field(default=GoalStatus.ACTIVE.value, description="The status of the goal")
    created_at: Optional[str] = Field(default=None, description="The start date of the goal")
    completed_date: Optional[str] = Field(default=None, description="The end date of the goal")
    # updated_at: str = Field(description="The end date of the goal")
    progress: Optional[float] = Field(default=None, description="The percentage progress of the goal")
    clear_chat :Optional[bool] = Field(default=None, description="Clear the chat")