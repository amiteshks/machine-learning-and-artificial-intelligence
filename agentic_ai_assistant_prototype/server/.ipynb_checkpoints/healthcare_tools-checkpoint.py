tools_list = [
    {
        "type": "function",
        "function": {
            "name": "discharge_patient",
            "description": "Discharge a Patient",
            "parameters": {
                "type": "object",  # Explicitly defining the type as "object"
                "properties": {  # Properties should be within this object
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID for the patient"
                    }
                },
                "required": ["patient_id"]  # Ensure "patient_id" is required
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_patient_status",
            "description": "Provide status of the patient",
            "parameters": {
                "type": "object",  # Explicitly defining the type as "object"
                "properties": {  # Properties should be within this object
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID for the patient"
                    }
                },
                "required": ["patient_id"]  # Ensure "patient_id" is required
            }
        }
    }
]


def discharge_patient(patient_id):
    print ("Starting discharge_patient process ")
    get_patient_discharge_status(patient_id)
    process_billing_information(patient_id)
    create_discharge_summary(patient_id)
    print ("Completed discharge_patient process ")
    return f"Discharge process completed for patient {patient_id}"

def get_patient_status(patient_id):
    print ("Starting get_patient_status ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    for i in range (3, 0, -1):
        print(i, "...")
    print ("Completed get_patient_status ")
    return f"Patient details for {patient_id}"


def get_patient_discharge_status(patient_id):
    print ("Starting get_patient_discharge_status ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    for i in range (3, 0, -1):
        print(i, "...")
    print ("Completed get_patient_discharge_status" )
    return f"Discharge status for {patient_id}"

def process_billing_information(patient_id):
    print ("Starting process_billing_information ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    for i in range (3, 0, -1):
        print(i, "...")
    print ("Completed process_billing_information" )
    return f"Billing information processed for {patient_id}"

def create_discharge_summary(patient_id):
    print ("Starting create_discharge_summary ")
    # In real code, this function woould be making an API or DB call to get patient infomration. For now it just print 5 to 1
    for i in range (5, 0, -1):
        print(i, "...")
    print ("Completing create_discharge_summary" )
    return f"Discharge summary created for {patient_id}"