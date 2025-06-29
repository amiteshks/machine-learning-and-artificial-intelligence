""" 
Install:
    pip install fastapi uvicorn openai python-dotenv

Run the server:
    uvicorn main:app --reload
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from processor import Processor

# Load env variables
load_dotenv(override=True)

# Initialize FastAPI app
app = FastAPI()

# Request schema
class ChatRequest(BaseModel):
    message: str

# API endpoint
@app.post("/chat")
def chat(request: ChatRequest):
    processor = Processor()
    response = processor.chatbot_process(request.message)
    return {"response": response}
