from openai import OpenAI
import json

from tool_agents import tools_list, discharge_patient
print("Enter your question or request:")
user_input = input().strip()
print("You entered: ", user_input)

print (user_input)
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools_list
)

try:
    # First check if there are any tool calls
    if response.choices[0].message.tool_calls:
        tool = response.choices[0].message.tool_calls[0]
        tool_name = tool.function.name
        tool_arguments = tool.function.arguments
        tool_id = tool.id
        
        # Add the assistant's message first
        messages.append(response.choices[0].message)
        
        # Parse and execute the tool
        data = json.loads(tool_arguments)
        response_message = ""
        if tool_name == 'discharge_patient':
            patient_id = data['patient_id']
            response_message = discharge_patient(patient_id)
        elif tool_name == 'get_patient_status':
            patient_id = data['patient_id']
            response_message = get_patient_status(patient_id)

        # Then add the tool response
        messages.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "name": tool_name,
            "content": response_message,
        })

        # Get the final response
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        print("Final response:", second_response.choices[0].message.content)
    else:
        # If no tool calls, just print the response
        print(response.choices[0].message.content)
except Exception as e:
    print(f"An error occurred: {str(e)}")