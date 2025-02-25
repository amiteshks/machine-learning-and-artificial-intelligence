from openai import OpenAI


client = OpenAI()

print("Enter your question or request:")
user_input = input().strip()
print("You entered: ", user_input)


response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Either answer a question or invoke the following tools:"\
          "discharge_patient(patient_id)"\
          "answer_billing_questions(billing_id)"
        },
        {"role": "user", "content": user_input}
    ]
)

# Define the tools discharge_patient(patient_id) and answer_billing_questions(billing_id)
# Give descriptions for these agebts so that they can be picked up
#


print (response)
try:
    print(response.choices[0].message.content)
except:
    print("No response from the assistant", response)





