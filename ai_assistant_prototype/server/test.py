from logging_utility import logger 
from workflow_processor import process_request

# request = "Discharge patient with id 2231018"
request = "get status for patient with id 222341"
# request = "Just give me the full form of WBC - I don not need any description or explanation"
# request = "Just give me the fullform of Covid 19 - I don not need any description or explanation"
# process_message_2(request)
# response = process_request(request)
# print ("******************")
# print(f"Final Response: {response}")
# print ("******************")

# First call

thread_id = 1008
result = process_request(request, thread_id=thread_id)
# If result["awaiting_confirmation"] is True, get confirmation from user
print ("******************")
print(f"Result: {result}")
print ("******************")

# # Second call with same thread_id
confirmation_result = process_request("yes", thread_id=thread_id)
print ("******************")
print(f"Confirmation result: {confirmation_result}")
print ("******************")
