from google import genai
from google.genai import types

sys_instruct = "You are a search query interpreter. Extract the essential search keywords from the following query and Return only the keywords which will be most useful to search the file, separated by spaces."
client = genai.Client(api_key='AIzaSyATzFXLi0fz4_1xXKMlpJAo760IBIVWWKo')

message = input("Enter your message here: ")
response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=types.GenerateContentConfig(
        system_instruction=sys_instruct,
        temperature=0.0,
    ),
    contents=message
)

print(response.text)
