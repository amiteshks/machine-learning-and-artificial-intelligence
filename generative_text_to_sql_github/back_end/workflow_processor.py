from langgraph.graph import StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


from logging_utility import logger


from database_utility import execute_query

import json



# In real life, we will replace this with dynamically created tools list from a Database    
tools_list = []

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
    # Invoke the LLM with tools
    logger.info(f"Starting assistant_node.state: {state}")
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(tools_list, parallel_tool_calls=False)

    # System message
    sys_msg = SystemMessage(content=
        """ You are an expert SQL generator for Snowflake Database. I have the following database schema:

        CREATE TABLE IF NOT EXISTS public.invoices (
            invoice_id STRING PRIMARY KEY,        -- Unique identifier for each invoice
            customer_name STRING,                 -- Customer name
            status STRING,                        -- Invoice status (OPEN, PAST DUE, CLOSED)
            due_date DATE,                        -- Invoice due date
            memo STRING,                          -- Memo field for additional notes (e.g., "Failed Payments")
            amount DECIMAL(15,2),                 -- Invoice amount
            open_amount DECIMAL(15,2),            -- Amount that is still open (not paid)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp for when the invoice was created
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Timestamp for when the invoice was last updated
        );

        Please convert the following natural language query into a SQL query, using the correct table and column names.

        Return the SQL query and its description in **JSON format** like this:
         {
        "sql": "SELECT ...",
        "description": "..."
        }
        Return the result as a raw JSON object with no markdown formatting, no triple backticks, and no explanation. Only output valid JSON.

    """)
    
    
    # process user requests
    response = llm_with_tools.invoke([sys_msg] + state["messages"])
          
    return_value = {"messages": state["messages"] + [response]}
    # Ensure assistant properly formats response
    return return_value

# Node 2: Tools node
def tools_node(state: MessagesState):
    """Node to execute tools."""
    logger.info(f"Starting tools_node.state: {state}")
    last_message = state["messages"][-1]
    parsed = json.loads(last_message.content)
    sql_query = parsed.get("sql")
    
    tool_message = execute_query(sql_query)
    return_value = {"messages": state["messages"] + [tool_message]}
    logger.info(f"Starting tools_node.state: {state}")
    return return_value
    

def create_workflow() -> StateGraph:
 
    workflow_builder = StateGraph(MessagesState)
    workflow_builder.add_node("ai_assistant_node", ai_assistant_node)   
    workflow_builder.add_node("tools_node", tools_node)
     
     # Define edges
    workflow_builder.set_entry_point("ai_assistant_node")   
 
    workflow_builder.add_edge(
        "ai_assistant_node",    
        "tools_node",
    )
   
    workflow = workflow_builder.compile()
  
    return workflow



def process_request(request: str, thread_id: str = None) -> str:
    # Use provided thread_id or create new one
    logger.info(f"process_request 0000")
    # thread_config = {"configurable": {"thread_id": thread_id}}
    human_message = [HumanMessage(content=request)]
    last_message = None
    workflow = get_workflow()
    # logger.info(f"Process_request.workflow config 1000: {thread_config}")
    
    # response = workflow.invoke({"messages": human_message}, thread_config)
    response = workflow.invoke({"messages": human_message})
    
    last_message = response["messages"][-1]
   
    return_value = json.loads(last_message.content).get("results", [])


    return return_value
