import os
import json
from typing import List
from enum import Enum
from datetime import date
from pydantic import BaseModel, Field

import openai
import instructor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from metadata import coachName2systemPrompt

# Load environment variables

load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
instructor_client = instructor.from_openai(client)

app = FastAPI(
    title="Coachable API",
    description="Backend API for Coachable APP",
    version="1.0.0"
)

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Task(BaseModel):
    description: str = Field(description="The description of the task")
    start_date: date = Field(description="The start date of the task")
    end_date: date = Field(description="The end date of the task")
    status: TaskStatus = Field(description="The status of the task")

class Goal(BaseModel):
    description: str
    start_date: date = Field(description="The start date of the goal")
    end_date: date = Field(description="The end date of the goal")
    tasks: List[Task] = Field(description="The tasks associated with the goal")

## Sample endpoint for reference, not used in the app, will be removed 
@app.post("/generate-answer/", response_model=Answer)
async def generate_answer(question_data: Question):
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or any other available model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question_data.question}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract the generated answer
        answer = response.choices[0].message.content
        
        return Answer(answer=answer)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/generate-answer-structured-output/", response_model=Answer)
async def generate_answer(question_data: Question):
    try:
        # Call OpenAI API
        response = instructor_client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=Goal,
        messages=[{"role": "user", "content": question_data.question}],
)      
        # Extract the generated answer
        answer = json.loads(response)
        
        return {"answer": answer}
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

## TODO: work in progress
@app.post("/goal_setting/", response_model=Answer)
async def goal_setting(user_id: str, coach_name: str):
    try:
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or any other available model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content":''}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract the generated answer
        answer = response.choices[0].message.content
        
        return Answer(answer=answer)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 