from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.errors import NodeInterrupt
from langgraph.types import Command

from logging_utility import logger
from datetime import datetime
from tool_agents import discharge_patient, get_patient_status
from IPython.display import Image, display

import json



# In real life, replace this with dynamically created tools list from a Database    
tools_list = [discharge_patient, get_patient_status]

# Create a Singleton global variable to store the workflow    
WORKFLOW = None

def get_workflow():
    global WORKFLOW
    if WORKFLOW is None:
        WORKFLOW = create_workflow()
    return WORKFLOW

### Nodes section

# Node 1: Assistant node
def assistant_node(state: MessagesState):
   # return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}
    # Invoke the LLM with tools
    logger.info(f"Starting assistant_node.state: {state}")
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(tools_list, parallel_tool_calls=False)

    # System message
    sys_msg = SystemMessage(content="""You are a helpful medical assistant. You can:
    1. Help discharge patients using discharge_patient(patient_id)
    2. Check patient status using get_patient_status(patient_id)
    """)
    
     # Check if we're returning from a confirmation
    last_message = state["messages"][-1:]
    # is_post_confirmation = any(
    #     isinstance(msg, HumanMessage) and msg.content.lower() == "yes" 
    #     for msg in last_message
    # )
    
    if (isinstance(last_message, HumanMessage) and last_message.content.lower() == "yes"):
               
        response = llm_with_tools.invoke([
            sys_msg,
            last_message,  # Original request
            HumanMessage(content="Confirmation received. Proceeding with discharge process.")
            ])
        return {"messages": state["messages"] + [response]}
            
    # Normal flow for new requests
    response = llm_with_tools.invoke([sys_msg] + state["messages"])
   
    last_message = response
    # TODO: To fix - Check if response has tool calls that need confirmation
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_calls = last_message.tool_calls
        for tool_call in tool_calls: 
        
            if 'discharge_patient' == tool_call['name']:
                # Add confirmation message right after the assistant's response
                return {"messages": state["messages"] + [response, 
                    SystemMessage(
                        content="Please confirm if you want to proceed with this action (yes/no)?",
                        additional_kwargs={
                            "awaiting_confirmation": True,
                            "pending_tool_calls": response.tool_calls
                        }
                    )
                ]}
    return_value = {"messages": state["messages"] + [response]}
    # Ensure assistant properly formats response
    return return_value

# Node 2: Confirmation node
def confirmation_node(state: MessagesState):
    """Node to request user confirmation."""
    
    logger.info(f"Starting confirmation_node.state: {state}")
    # If the last message is to require confirmation, raise an exception to interrupt the workflow
    # else check if the last message is a Human confirmation message
    # Check if that message is continue, if yes - continue, else cancel and return to assistant node
    return_value = ""
    last_message = state["messages"][-1]
    # tool_calls = last_message.tool_calls  
    confirmation_messages = []
    # confirmation_keywords = ["yes", "confirm", "proceed", "ok", "sure", "go ahead"]
    
    if (isinstance(last_message, SystemMessage) and 
        last_message.additional_kwargs.get("awaiting_confirmation")):
        confirmation_messages = last_message.content
        logger.info(f"Node Interrupt with state: {state}")
        raise NodeInterrupt(f"Need confirmation: {confirmation_messages}")
    
    elif (isinstance(last_message, HumanMessage) and last_message.content.lower() == "yes"):
        confirmation_messages = last_message.content
        

    return {"messages": state["messages"] + confirmation_messages}


def tools_node(state: MessagesState):
    """Node to execute tools."""
    logger.info(f"Starting tools_node.state: {state}")
    last_message = state["messages"][-1]
    
    # Check if the last message has tool_calls
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        logger.warning("No tool calls found in last message")
        return {"messages": state["messages"]}
    
    tool_calls = last_message.tool_calls
    from tool_agents import get_patient_status, discharge_patient
    
    tool_messages = []
    for tool_call in tool_calls:
        tool_name = tool_call["name"] # Access the function name correctly
        tool_args = tool_call["args"]  # Parse JSON arguments
        
        tools_map = {
            "discharge_patient": discharge_patient,
            "get_patient_status": get_patient_status
        }
        
        tool_func = tools_map.get(tool_name)
        if tool_func:
            try:
                result = tool_func(**tool_args)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call["id"], 
                    "name": tool_name,
                    "content": str(result)
                }
                tool_messages.append(tool_message)
                logger.info(f"Tool response: {tool_message}")
            except Exception as e:
                error_message = f"Error executing tool: {str(e)}"
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "content": error_message
                })
                logger.error(error_message)

    # Make sure we're only adding tool messages if there were actual tool calls
    if tool_messages:
        return {"messages": state["messages"] + tool_messages}
    return {"messages": state["messages"]}

### Conditions section
#Condition 1: Check if a tool call requires confirmation node?  
def is_confirmation_node_required_condition(state: MessagesState):
    
    last_message = state["messages"][-1]
    logger.info(f"Starting is_confirmation_node_required_condition.last_message: {last_message}")
    return_value = "to_end"
    # DELETE confirmation_messages = []

    if isinstance(last_message, SystemMessage):
        if last_message.additional_kwargs["awaiting_confirmation"]:
            return_value = "proceed_to_confirmation_node"
        else:
            return_value = "proceed_to_tools_node"    
    
    return return_value
    

# Condition 3: Should route to tools node?  
def should_route_to_tools(state: MessagesState):
    """Custom condition to determine if we should route to tools or end."""
    last_message = state["messages"][-1]    
    logger.info(f"Starting should_route_to_tools.last_message: {last_message}")
    # If the last message is a tool call, route to the tools node
    # if hasattr(last_message, "tool_calls"):
            # Instead of hasattr(), check if tool_calls exists and is not None/empty
    if getattr(last_message, "tool_calls", None):
        return "proceed_to_tools_node"
    return "to_end"



def create_workflow() -> StateGraph:
    # Initialize LLM
  
    # Build workflow graph
    workflow_builder = StateGraph(MessagesState)
    workflow_builder.add_node("assistant_node", assistant_node)
    workflow_builder.add_node("confirmation_node", confirmation_node)
    workflow_builder.add_node("tools_node", tools_node)
     
     # Define edges
    workflow_builder.add_edge(START, "assistant_node")
     # Add confirmation flow
    workflow_builder.add_conditional_edges(
        "assistant_node",
        is_confirmation_node_required_condition,
        {
            "proceed_to_confirmation_node": "confirmation_node", # e.g. discharge patient 
            "proceed_to_tools_node": "tools_node", # e.g. get patient status
            "to_end": END,
        }
    )
    # After confirmation, go back to assistant
    workflow_builder.add_edge("confirmation_node", "assistant_node")
    
    # After tools, go back to assistant
    workflow_builder.add_edge("tools_node", "assistant_node")
       
    memory = MemorySaver()
    workflow = workflow_builder.compile(checkpointer=memory)

    # graph_png = workflow.get_graph().draw_mermaid_png()
    # with open(f"workflow_graph.png", "wb") as f:
    #     f.write(graph_png)

    return workflow


def process_request_0(request: str) -> str:
    
    # thread_id = str(datetime.now().timestamp())
    thread_id = "1740380952.242586"
    config = {"configurable": {"thread_id": thread_id}}
    
    response = [HumanMessage(content=request)]

    workflow = get_workflow()
    logger.info(f"Process_request.workflow config: {config}")

    response = workflow.invoke({"messages": response}, config)  
    last_message = response["messages"][-1].content if response["messages"] else "No response from the assistant"
    logger.info(f"Response generated: {last_message[:100]}...")  # Log first 100 chars of response
    logger.info(f"Thread_id: {thread_id}")
    return {"response": last_message} 

from typing import List, Dict
from collections import defaultdict
THREAD_MESSAGES = defaultdict(list)
  
def process_request(request: str, thread_id: str = None) -> str:
    # Use provided thread_id or create new one
    if thread_id is None:
        thread_id = str(datetime.now().timestamp())
    
    config = {"configurable": {"thread_id": thread_id}}
    response = [HumanMessage(content=request)]
    
    workflow = get_workflow()
    logger.info(f"Process_request.workflow config: {config}")

    try:
        response = workflow.invoke({"messages": response}, config)
        logger.info(f"Response generated: {response}")
    except NodeInterrupt as e:
        # Return both the interruption message and thread_id so the client knows to continue this thread
        return e
    
    THREAD_MESSAGES[thread_id] = response["messages"]    
    return response
