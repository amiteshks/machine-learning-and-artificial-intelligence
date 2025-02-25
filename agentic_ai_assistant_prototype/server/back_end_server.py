from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from logging_utility import logger
from datetime import datetime
import uuid
# from langgraph_workflows_manager import process_request
from langgraph_utilities.workflow_processor import process_request
import os
from logging.handlers import RotatingFileHandler
from logging_utility import logger
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
from collections import defaultdict




#LangChain Project form LangSmith Tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "AgenticAI-POC-Feb22"

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


@app.post("/process-audio")
async def process_request_audio(request: Request, audio: UploadFile = File(...)):
    client_id = request.client.host if hasattr(request, 'client') else 'default'
    thread_id = thread_store[client_id]
    
    logger.info(f"Received audio request. thread_id is {thread_id}")

    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_webm = os.path.join(temp_dir, "temp_audio.webm")
        temp_wav = os.path.join(temp_dir, "temp_audio.wav")
        try:
            # Save the uploaded WebM file
            with open(temp_webm, "wb") as buffer:
                content = await audio.read()
                buffer.write(content)
            
            # Convert WebM to WAV using pydub
            audio_segment = AudioSegment.from_file(temp_webm, format="webm")
            audio_segment.export(temp_wav, format="wav")
            
            # Process the WAV file
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_wav) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                logger.info(f"Transcribed text: {text}")
                # response = process_message(text)
                
                llm_response = process_request(text)
                
                logger.info(f"Response: {llm_response}")
                # logger.info(f"Response: {llm_response['response']}")
                # response = llm_response['response'] + "<br/><br/><b> You requested: </b>" + text
                # logger.info(f"response: {response}")
                return llm_response
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return {"response": f"Error processing audio: {str(e)}"}
