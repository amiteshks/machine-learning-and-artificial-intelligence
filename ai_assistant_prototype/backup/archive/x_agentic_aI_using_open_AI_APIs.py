# Import required libraries
from openai import OpenAI
import json
from server.tool_agents import tools_list, discharge_patient, get_patient_status

# Get user input
print("Enter your question or request:")
user_input = input().strip()
print("You entered: ", user_input)
print(user_input)

# Initialize OpenAI client
client = OpenAI()

# Set up the initial conversation messages
messages = [
    # System message defines the AI's role and available tools
    {"role": "system", "content": "You are a helpful assistant. Either answer a question or invoke the following tools:"\
          "discharge_patient(patient_id)"\
          "get_patient_status(patient_id)"
    },
    # Add the user's input to the conversation
    {"role": "user", "content": user_input}
]

# Make the initial API call to OpenAI
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools_list
)

try:
    # Check if the assistant wants to use any tools
    if response.choices[0].message.tool_calls:
        # Extract tool call information. 
        tool = response.choices[0].message.tool_calls[0]
        tool_name = tool.function.name
        tool_arguments = tool.function.arguments
        tool_id = tool.id
        
        # Add the assistant's response to the conversation history
        messages.append(response.choices[0].message)
        
        # Parse the tool arguments and execute the appropriate function
        data = json.loads(tool_arguments)
        response_message = ""
        if tool_name == 'discharge_patient':
            patient_id = data['patient_id']
            response_message = discharge_patient(patient_id)
        elif tool_name == 'get_patient_status':
            patient_id = data['patient_id']
            response_message = get_patient_status(patient_id)

        # Add the tool's response to the conversation
        messages.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "name": tool_name,
            "content": response_message,
        })

        # Make a second API call to get the assistant's final response
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        print("Final response:", second_response.choices[0].message.content)
    else:
        # If no tools were called, print the direct response
        print(response.choices[0].message.content)

# Error handling
except Exception as e:
    print(f"An error occurred: {str(e)}")