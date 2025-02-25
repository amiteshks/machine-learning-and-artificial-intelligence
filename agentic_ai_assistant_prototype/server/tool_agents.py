from logging_utility import logger


def discharge_patient(patient_id: str) -> str:
    """Discharge a patient from the hospital given their patient ID.

    Args:
        patient_id: the patient ID of the patient to discharge
    """
    
    # logger.info ("Starting discharge_patient process ")
    get_patient_discharge_status(patient_id)
    process_billing_information(patient_id)
    create_discharge_summary(patient_id)
    logger.info ("Completed discharge_patient process ")
    return f"Discharge process completed for patient {patient_id}. Please find the discharge summary below"
  

def get_patient_status(patient_id: str) -> str:
    """Get the status of a patient given their patient ID.

    Args:
        patient_id: the patient ID of the patient to get the status of
    """
    logger.info ("Starting get_patient_status ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    for i in range (3, 0, -1):
        print(i, "...")
    logger.info ("Completed get_patient_status ")
    return f" Patient {patient_id} is feeling good and is in room 123"


def get_patient_discharge_status(patient_id):
    logger.info ("Starting get_patient_discharge_status ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    # for i in range (3, 0, -1):
    #     print(i, "...")
    logger.info ("Completed get_patient_discharge_status" )
    return f"Discharge status for {patient_id}"

def process_billing_information(patient_id):
    # logger.info ("Starting process_billing_information ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    # for i in range (3, 0, -1):
    #     print(i, "...")
    logger.info ("Completed process_billing_information" )
    return f"Billing information processed for {patient_id}"

def create_discharge_summary(patient_id):
    # logger.info ("Starting create_discharge_summary ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    # for i in range (5, 0, -1):
    #     print(i, "...")
    logger.info ("Completing create_discharge_summary" )
    return f"Discharge summary created for {patient_id}"

# tools_list = [
#     {
#         "type": "function",
#         "function": {
#             "name": "discharge_patient",
#             "description": "Discharge a Patient",
#             "parameters": {
#                 "type": "object",  # Explicitly defining the type as "object"
#                 "properties": {  # Properties should be within this object
#                     "patient_id": {
#                         "type": "string",
#                         "description": "Patient ID for the patient"
#                     }
#                 },
#                 "required": ["patient_id"]  # Ensure "patient_id" is required
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_patient_status",
#             "description": "Provide status of the patient",
#             "parameters": {
#                 "type": "object",  # Explicitly defining the type as "object"
#                 "properties": {  # Properties should be within this object
#                     "patient_id": {
#                         "type": "string",
#                         "description": "Patient ID for the patient"
#                     }
#                 },
#                 "required": ["patient_id"]  # Ensure "patient_id" is required
#             }
#         }
#     }
# ]
