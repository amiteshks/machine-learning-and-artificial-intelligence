from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
# from langgraph import AgentGraph, Tool
from langgraph.graph import StateGraph
import openai
import logging
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage

from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

from langchain_openai import ChatOpenAI  #   LangChain: OpenAI Chat Model
from langchain_core.messages import SystemMessage, HumanMessage  #   LangChain: Message Handling
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


app = FastAPI()

# Allow requests from frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Define user input model
class UserRequest(BaseModel):
    user_input: str

# Define agent behavior (Example: LLM calling function)
def llm_agent(input_text):
  
    llm = ChatOpenAI(model="gpt-4o-mini")
    messages = [
        SystemMessage(content="You are an AI assistant.. "),
        HumanMessage(content=input_text),
    ]
    response = llm.invoke(messages) 
    return response.content



@app.post("/process")
async def process_request(request: UserRequest):
    response = graph.invoke(request.user_input)
    return {"response": response}



class State(str):
    str
    

# def front_end_llm_node(str) :
#     print ("---front_end_llm_node---")
#     # return {"graph_state": state['user_text']}
#     return {"response":"Back"}
# def llm_agent(input_text):
#     response = openai.ChatCompletion.create(
#         model="gpt-4-turbo",
#         messages=[{"role": "system", "content": "You are an AI assistant."},
#                   {"role": "user", "content": input_text}]
#     )
#     return response["choices"][0]["message"]["content"]

# def front_end_llm_node() :
#     print ("---front_end_llm_node---")
#     return {"graph_state": state['user_text']}
    
    

# Define a sample agent graph
# graph = AgentGraph()
builder = StateGraph(str)
builder.add_node("llm_agent", llm_agent)
builder.add_edge(START, "llm_agent")
# graph.add_node("assistant", assistant)
# builder.add_node("tools", ToolNode(tools))
# graph.add_tool(Tool(name="AI_Assistant", function=llm_agent))

graph = builder.compile()

# View
display(Image(graph.get_graph().draw_mermaid_png()))


graph.invoke("What's France's capital?")