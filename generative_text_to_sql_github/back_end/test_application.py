from workflow_processor import process_request
from logging_utility import logger

  
def test_tools_flow(thread_id: str):
    # Test message
    test_message = " List all invoices that are due next week"
  
    # Process the request through the workflow
    result = process_request(test_message)
    logger.info(f"Workflow Result: {result}")



def main():
    thread_id = "test_thread_123"
    test_tools_flow(thread_id)

if __name__ == "__main__":
    main()
  

