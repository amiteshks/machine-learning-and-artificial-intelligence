from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from logging_utility import logger
from datetime import datetime
import uuid
# from langgraph_workflows_manager import process_request
from workflow_processor import process_request
import os
from logging.handlers import RotatingFileHandler
from logging_utility import logger
from collections import defaultdict




#LangChain Project form LangSmith Tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "AgenticAI-POC"


#Create FastAPI app and add CORS middleware to allow requests from the frontend
app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restrict to known domains
    allow_credentials=True,  # Enable only if required
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Restrict methods
    allow_headers=["Content-Type", "Authorization"],  # Limit headers
)

# **** Process Inbound Post Request ****
# Define request model
class UserRequest(BaseModel):
    user_input: str

# Global thread store
thread_store = defaultdict(lambda: str(uuid.uuid4()))

# Process Inbound Post Request 
@app.post("/process")
async def process_message_text(request: UserRequest):
    client_id = request.client.host if hasattr(request, 'client') else 'default'
    thread_id = thread_store[client_id]
    
    logger.info(f"Received request: {request.user_input}. thread_id is {thread_id}")

    try:
        
        # Pass user message to  process_request function and return the response
        request_str = request.user_input
        response = process_request(request_str, thread_id=thread_id)
        
        return response     
    except Exception as e:
        logger.info(f"Error processing request: {str(e)}")
        raise
