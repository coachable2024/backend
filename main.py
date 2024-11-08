from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="Question Answering API",
    description="API that generates answers using OpenAI's GPT model",
    version="1.0.0"
)

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 