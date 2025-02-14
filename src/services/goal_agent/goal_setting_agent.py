from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from src.schemas.goal.goal_models import Goal
from src.services.goal_agent.goal_setting_agent_prompt import goal_tagging_prompt, TaskExample, GoalExample, PlanExample
from typing import List, Optional, Any
from openai import OpenAI
import os
import redis
import instructor

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

class WorkFlowManagerData(BaseModel):
    goal: Goal = Goal()
    chat_history: List[Any] = []


class GoalSettingAgent:
    openai_client = OpenAI(api_key="")
    instructor_client = instructor.from_openai(openai_client)
    MODEL = "gpt4o-mini"
    def __init__(self, workflow_manager_data:WorkFlowManagerData=WorkFlowManagerData()):
        self.workflow_data = workflow_manager_data

    def tag_goal(self):
        last_asked_ai_question = self.workflow_data.chat_history[-1]
        tagging_prompt = goal_tagging_prompt.format(chat_history = self.workflow_data.chat_history,
                       last_asked_ai_question = last_asked_ai_question,
                       habits = self.workflow_data.goal.habits,
                       hours = self.workflow_data.goal.hours_dedicated,
                       current_date = self.current_date,
                       TaskExample = TaskExample,
                       GoalExample = GoalExample,
                       PlanExample = PlanExample,)
        tagged_info = self.instructor_client.chat.completions.create(
                                model= self.MODEL,
                                response_model=Goal,
                                messages=[{"role": "system", 
                                            "content": tagging_prompt },
                                        {"role": "user", "content": user_input}],
                                temperature=0
                                ) 



    def generate_response(self, user_input):
        # tagging
        


