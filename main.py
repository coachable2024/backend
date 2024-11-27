from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from datetime import date
from pydantic import Field
from enum import Enum
import openai
import os
from typing import List
import instructor
import json
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Patch the OpenAI client
instructor_client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))

app = FastAPI(
    title="Question Answering API",
    description="API that generates answers using OpenAI's GPT model",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str | dict


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

# Add this date serializer class
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, TaskStatus):
            return obj.value
        return super().default(obj)

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
        response = instructor_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_model=Goal,
            messages=[{"role": "user", "content": question_data.question}],
        )      
        # Convert to JSON string with custom encoder
        answer_json = json.dumps(response.dict(), cls=DateEncoder)
        
        return Answer(answer=answer_json)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 