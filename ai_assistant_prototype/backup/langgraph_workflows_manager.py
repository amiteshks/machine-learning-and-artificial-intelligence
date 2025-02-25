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
def ai_assistant_node(state: MessagesState):
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
    # process user requests
    response = llm_with_tools.invoke([sys_msg] + state["messages"])
   
    last_message = response
    
    return_value = {"messages": state["messages"] + [response]}
    
    # Ensure assistant properly formats response
    return return_value

# Node 2: Tools node
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
    

# Condition 1: Should route to tools node?  
def should_route_to_tools(state: MessagesState):
    """Custom condition to determine if we should route to tools or end."""
    last_message = state["messages"][-1]    
    logger.info(f"Starting should_route_to_tools.last_message: {last_message}")
    
    if getattr(last_message, "tool_calls", None):
        return "proceed_to_tools_node"
    return "to_end"



def create_workflow() -> StateGraph:
    # Initialize LLM
  
    # Build workflow graph
    workflow_builder = StateGraph(MessagesState)
    workflow_builder.add_node("ai_assistant_node", ai_assistant_node)   
    workflow_builder.add_node("tools_node", tools_node)
     
     # Define edges
    workflow_builder.add_edge(START, "ai_assistant_node")   
     # Add confirmation flow
    workflow_builder.add_conditional_edges(
        "ai_assistant_node",    
        should_route_to_tools,
        {
            
            "proceed_to_tools_node": "tools_node", # e.g. get patient status
            "to_end": END,
        }
    )

    
    # After tools, go back to assistant
    workflow_builder.add_edge("tools_node", "ai_assistant_node")
       
    memory = MemorySaver()
    workflow = workflow_builder.compile(checkpointer=memory)

    graph_png = workflow.get_graph().draw_mermaid_png()
    with open(f"workflow_graph.png", "wb") as f:
        f.write(graph_png)

    return workflow



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
        last_message = response["messages"][-1].content if response["messages"] else "No response from the assistant"
        logger.info(f"Response generated: {last_message[:100]}...")  # Log first 100 chars of response
        logger.info(f"Response generated: {response}")
    except NodeInterrupt as e:
        # Return both the interruption message and thread_id so the client knows to continue this thread
        return e
    

    return last_message
