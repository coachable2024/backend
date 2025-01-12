import os
import json
from typing import List, Optional, Any, Dict, Literal
from enum import Enum
from datetime import date
import pandas as pd
import sys

import uvicorn
import openai
import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

import duckdb

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key="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")
instructor_client = instructor.from_openai(client)
MODEL = "gpt-4o" # or any other available model

app = FastAPI(
    title="Coachable API",
    description="Backend API for Coachable APP",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Redis connection parameters
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True  # Automatically decode responses to strings
)

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str | dict

class HistoryRecord(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    user_input: str
    coach_name: str
    history: List[HistoryRecord] = Field(default_factory=list)


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

class Task(BaseModel):
  id: Optional[str] = Field(default=None, description="The id of the task")
  category: Literal["Goal_Related_Task"] = Field(description="This is a goal related task")
  title: Optional[str] = Field(default=None, description="The title of the task")
  description: Optional[str] = Field(default=None, description="The description of the task")
  frequency : Optional[str] = Field(default='Daily', description="The frequency of the habit")
  preferred_time : Optional[str] = Field(default=None, description="The preferred time to do this task daily, the format should be '%H:%M'")
  duration: Optional[int] = Field(default=None, le = 24, ge = 0, description="The duration of this task, the unit is hour. ")
  completed_date: Optional[str] = Field(default=None, description="The dates that users complete this task.")
#   scheduled_dates: Optional[str] = Field(default=None, description="The title of the habit")
  status: Optional[str] = Field(default='Active', description="The status of the task, can be active or inactive")
#   created_at: Optional[str] = Field(default=None, description="The title of the habit")
#   updated_at: Optional[str] = Field(default=None, description="The title of the habit")
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
  completed_dates: Optional[str] = Field(default=None, description="The dates that users have completed this habits' activities.")
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
    # progress: Optional[float] = Field(default=None, description="The percentage progress of the goal")
    clear_chat :Optional[bool] = Field(default=None, description="Clear the chat")

class AnswerWithHistory(BaseModel):
    answer: str
    history: List[HistoryRecord]
    goal: Optional[Goal]

class WorkFlowManager(BaseModel):
    goal: Goal = Goal()
    chat_history: List[Any] = []


# Add this date serializer class
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, TaskStatus):
            return obj.value
        if isinstance(obj, GoalStatus):
            return obj.value
        if isinstance(obj, GoalCategory):
            return obj.value
        return super().default(obj)

@app.post("/goal_setting_chat/", response_model=AnswerWithHistory)
async def generate_answer(request_body: ChatInput):
    user_input = request_body.user_input
    user_id = 'test123'
    
    # Get data from Redis
    workflow_data_dict = await redis_client.get(user_id)
    print("\n =========== Workflow_data STARTING STATUS ===========")
    print(workflow_data_dict)
    
    # Initialize workflow_data
    workflow_data = WorkFlowManager()
    
    # Only try to parse JSON if we got data from Redis
    if workflow_data_dict is not None:
        # try:
        workflow_data_dict = json.loads(workflow_data_dict)
        workflow_data = WorkFlowManager(**workflow_data_dict)
        # except json.JSONDecodeError:
            # Handle invalid JSON data
    
    # Set basic properties
    workflow_data.goal.user_id = user_id
    workflow_data.goal.id = 'goal1'
    workflow_data.goal.created_at = date.today().strftime("%Y-%m-%d")
    
    # tag the goal and tasks in the response
    if len(workflow_data.chat_history):
        last_asked_ai_question = workflow_data.chat_history[-1]
    else:
        last_asked_ai_question = 'just started'
    
    tagging_prompt = """
                You are a life coach helping the client to set a goal and help them achieve the goal.
                You need to discuss with client what goal they want to set, and understand their daily routine and habits, then break down the goal to daily tasks, and plan the time works for their daily schedules.
                You are a tagging agent, so your primary responsibility is to tag information in pydantic model **Goal** based on user input and your planning experties.
                Only tag the field when user input is clear. Do not tag the field when user input is ambiguous, and you cannot determine the value.
                Do not tag None values to any fields. 

                If users say "Clear the chat", tag **clear_chat** as True.
                You are provided with {chat_history}, review the chat history, and the last ai asked question: {last_asked_ai_question}. Identify which steps in the goal setting workflow are we, and identify which fields are users talk about, tag those fields accordingly.
                    Step 1: communicate with the client about what their goal is and clarify as needed. Tag the goal title and description in this step.
                    Step 2: discuss with the client the due date to achieve the goal. Tag the goal target date in this step.
                    Step 3: ask users how many hours do they want to dedicate to the goal for completing the related tasks.
                    Step 4: Ask user if they want to confirm the goal they are setting.
                    Step 5: In order to understand their daily schedule, ask if they want to add daily routine or habits to help AI schedule the tasks, if they do, then tag the habit lists. 
                        Step5.1: Ask the habit title, description.
                        Step5.2: The preferred time they want to do this habit daily, the format should be '%H:%M'", and ask them about how long do they want to do this habit daily, and tag the duration properly. Do not assume any values.
                    Step 6: Ask if clients want to confirm the habits.
                    Step 7: With the confirmed goal and habits, it is your job to break down the goal into concrete and actionable tasks that suits their daily schedules. Break down the goal to a list of task in this step, it cannot be an empty list.
                            Step6.1. Refer to the habits user need to do everyday: {habits}. How many hours they want to dedicated to the goal to complete related tasks {hours}. Then plan the schedules of the tasks. Find the best time in a day to plan these tasks. Tag the preferred time cleverly.
                            Step6.2: Tag all the fields of tasks. Give detailed title and descriptions of the task, especially any fields related to the time. Tasks cannot be an empty list in this step.
            """.format(chat_history = workflow_data.chat_history,
                       last_asked_ai_question = last_asked_ai_question,
                       habits = workflow_data.goal.habits,
                       hours = workflow_data.goal.hours_dedicated)
    response = instructor_client.chat.completions.create(
                            model=MODEL,
                            response_model=Goal,
                            messages=[{"role": "system", 
                                        "content": tagging_prompt },
                                    {"role": "user", "content": user_input}],
                        ) 
    
    # Convert to JSON string with custom encoder
    tagged_goal = response.dict()

    print('\n =========== answerjson =========== ', flush = True)
    print(tagged_goal)

    tasks = tagged_goal.get('tasks')
    habits = tagged_goal.get('habits')
    clear_chat = tagged_goal.get('clear_chat')

    if clear_chat:
        workflow_data = WorkFlowManager()
        await redis_client.set(user_id, json.dumps(workflow_data.dict()))
        return AnswerWithHistory(answer='cleared', history=[], goal=None)
   
    for key, value in tagged_goal.items():
        if value is not None:
            if key not in  ['tasks', 'habits']:
                try:
                    setattr(workflow_data.goal, key, value)
                except:
                    pass
    
    if tasks and len(tasks):
        for temp_task in tasks:
            print('\n =========== temp task ===========')
            print(temp_task)
            try:
                workflow_data.goal.tasks.append(Task(**temp_task))
            except:
                pass
    
    if habits and len(habits):
        for temp_habit in habits:
            print("\n ===========temp habits===========")
            print(temp_habit)
            try:
                workflow_data.goal.habits.append(Habit(**temp_habit))  
            except:
                pass     

    print('\n =========== workflow data after tagging===========')
    print(workflow_data.goal)
    # try:
    goal_dict_data = workflow_data.goal.dict()
    fields_values_to_gather = []
    for key, value in goal_dict_data.items():
        if key not in ['id','user_id' ,'status', 'created_at', 'completed_date', 'progress']:
            if value is None:
                fields_values_to_gather.append(key)

    print("\n =========== fields to gather ===========")
    print(fields_values_to_gather)
    key = fields_values_to_gather[0]
    if key in ['title', 'description']:
        information_to_gather = 'Please provide the title and describe your goal.'
    elif key in ['target_date']:
        information_to_gather = "Ok we will start to work towards to this goal today, let's dicuss when do we want to achieve this goal, please provide a datetime."
    elif key in ['hours_dedicated']:
        information_to_gather = "How many hours do you want to dedicate to this goal every day?"
    elif key in ['confirm_goal']:
        information_to_gather = "Let's review our goal and confirm the goal description, due date, and dedicated time."
    elif key  == 'add_habits':
        information_to_gather = "Do you want to add any daily routines or habits? This will help us plan the tasks regarding to the goal for you."
    elif key == 'habits':
        information_to_gather = "Let's plan the habits. Can you provide the habit title and description? What is the preferred time you want to do this habit daily,  and ask them about how long do they want to do this habit daily."
    elif key == "confirm_tasks":
        information_to_gather = "Please confirm the tasks"
    else:
        information_to_gather = "The goal has been set, if you need other help, let me know!"

    print("\n=========== information_to_gather ===========")
    print(information_to_gather)
    # ai response
    system_prompt = """
            You are a life coach helping the client to set a goal and help them achieve the goal.
            You need to discuss with client what goal they want to set, and understand their daily routine and habits, then break down the goal to daily tasks, and plan the time works for their daily schedules.
            You are the life coach agent generate response for users, your primary responsibility is to guide users to set the goals, understand their daily scheudles(habit), and help plan their tasks.
            You are provided with {chat_history}, review the chat history, identify which steps in the goal setting workflow are we: 
            Here is the goal setting and task planning workflow: 
        Step 1: communicate with the client about what their goal is and clarify as needed. Tag the goal title and description in this step.
        Step 2: discuss with the client the due date to achieve the goal. Tag the goal target date in this step.
        Step 3: ask users how many hours do they want to dedicate to the goal for completing the related tasks.
        Step 4: Ask user if they want to confirm the goal they are setting.
        Step 5: In order to understand their daily schedule, ask if they want to add daily routine or habits to help AI schedule the tasks, if they do, then tag the habit lists. 
            Step5.1: Ask the habit title, description.
            Step5.2: The preferred time they want to do this habit daily, the format should be '%H:%M'", and ask them about how long do they want to do this habit daily, and tag the duration properly. Do not assume any values.
        Step 6: Ask if clients want to confirm the habits.
        Step 7: With the confirmed goal and habits, it is your job to break down the goal into concrete and actionable tasks that suits their daily schedules. Break down the goal to a list of task in this step, it cannot be an empty list.
                Step6.1. Refer to the habits user need to do everyday: {habits}. How many hours they want to dedicated to the goal to complete related tasks {hours}. Then plan the schedules of the tasks. Find the best time in a day to plan these tasks. Tag the preferred time cleverly.
                Step6.2: Tag all the fields of tasks. Give detailed title and descriptions of the task, especially any fields related to the time. Tasks cannot be an empty list in this step.
        **Special Instruction of the response**
        - You are provided with the information we need to gather specifically in this response, ask questions related to this:
        {information_to_gather}
        - When you identify AI has been finished planning the task: {tasks}, and it is is not an empty list, in your reply, please show to the user the planned tasks.
        - Whenever users have issues understanding goal or tasks, or need emotional support, tackle those first, them gracefully guide them to the goal setting workflow.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", 
                "content": system_prompt.format(information_to_gather = information_to_gather, 
                                                chat_history = workflow_data.chat_history,
                                                habits = workflow_data.goal.habits,
                                                tasks = workflow_data.goal.tasks,
                                                hours = workflow_data.goal.hours_dedicated,)},
            {"role": "user", "content": user_input}],
        max_tokens=500,
        temperature=0.7
    )
    answer = response.choices[0].message.content
    workflow_data.chat_history.append({'role': 'user', 
                                    'content': user_input})
    # append to chat history
    workflow_data.chat_history.append({'role': 'assistant', 
                                    'content': answer})
    # save data to redis

    print("\n -----workflow data-----")
    print(workflow_data.dict())
    await redis_client.set(user_id, json.dumps(workflow_data.dict()))
    # except Exception as e:
    #     print(str(e))
    #     answer = 'wrong'
    print(workflow_data)

    print('\n ========= give answer to the user ============')
    print(answer)

    # try:
    return AnswerWithHistory(answer=answer, history=workflow_data.chat_history, goal=workflow_data.goal)
    # except openai.APIError as e:
    #     raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


## Sample endpoint for reference, not used in the app, will be removed 
# @app.post("/generate-answer/", response_model=Answer)
# async def generate_answer(question_data: Question):
#     try:
#         # Call OpenAI API
#         response = client.chat.completions.create(
#             model=MODEL,  
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": question_data.question}
#             ],
#             max_tokens=500,
#             temperature=0.7
#         )
        
#         # Extract the generated answer
#         answer = response.choices[0].message.content
        
#         return Answer(answer=answer)
    
#     except openai.APIError as e:
#         raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# @app.get("/get_goal/")
# async def get_goal():
#     user_id = "123"
#     # goal_result = duckdb.sql("SELECT * FROM 'goal_temp.json' where user_id == {}".format(user_id))
#     # task_result = duckdb.sql("SELECT * FROM 'task_temp.json' where user_id == {}".format(user_id))
#     # add data to duckdb
#     conn = duckdb.connect()
#     conn.execute("""
#     CREATE TABLE IF NOT EXISTS tasks AS
#     SELECT * FROM read_json_auto(?)
#     """, ['task_temp.json'])
    
#     # Verify data loaded
#     df = conn.execute("SELECT * FROM tasks").fetchdf()
#     print("Existing Data:")
#     print(df)
#     # temp_goals = pd.read_json("goal_temp.json", lines=True)
#     temp_tasks = pd.read_json("task_temp.json")
#     print(temp_tasks)
#     print("temp_tasks:")
#     print(temp_tasks.values.tolist())
#     conn.execute("""
#         INSERT INTO tasks (id, title, description, status, updated_at, created_at, priority, start_date, due_date, start_time, end_time, duration)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, temp_tasks.values.tolist())

#     print("New users inserted successfully.")

#     df_updated = conn.execute("SELECT * FROM tasks").fetchdf()
#     print(df_updated)
#     return df_updated
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000) 

