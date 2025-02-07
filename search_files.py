# search_files.py
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from google import genai
from google.genai import types
from whoosh.qparser import QueryParser, AndGroup, OrGroup
from whoosh.qparser import MultifieldParser

sys_instruct = "You are a search query interpreter. Extract the essential search keywords from the following query and Return only the keywords which will be most useful to search the file, separated by spaces."
client = genai.Client(api_key='AIzaSyATzFXLi0fz4_1xXKMlpJAo760IBIVWWKo')
result_found = False
# Open the index
ix = open_dir("indexdir")

# Set up a query parser for the 'content' field
# Use MultifieldParser to search in both 'file_name' and 'content'
# Here we boost the 'file_name' field by 2.0 to prioritize matches there
fields = ["file_name", "content"]
fieldboosts = {"file_name": 2.0, "content": 1.0}
parser = MultifieldParser(fields, schema=ix.schema,
                          group=OrGroup, fieldboosts=fieldboosts)

# Prompt the user for a query
query_str = input("Enter your search query: ")

response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=types.GenerateContentConfig(
        system_instruction=sys_instruct,
        temperature=0.0,
    ),
    contents=query_str
)

# Parse the query
query = parser.parse(response.text)

# Search the index and display results
with ix.searcher() as searcher:
    results = searcher.search(query, limit=20)  # Adjust limit as needed
    numberOfResults = len(results)
    print(f"\nFound {numberOfResults} result(s):")
    if numberOfResults > 0:
        result_found = True

    for hit in results:
        print(f"File: {hit['file_name']}")
        print(f"Path: {hit['file_path']}\n")

# Nova
novaPersonality = '''
You are **Nova**, an AI-powered knowledge base with a warm, professional, and curious personality.  

You will be provided with three input parameters:  
1. **Search Query** (string) – The term or phrase the user is searching for.  
2. **Results Found** (True/False) – Indicates whether relevant files were located.  
3. **Number of Results** (integer) – The count of relevant results found.  

### **Your Task:**  
Based on the input parameters, craft an appropriate response:  
- **If results are found** → Acknowledge the search success.  
- **If no results are found** → Politely inform the user and suggest alternative approaches, such as refining the search query.  

Maintain a **warm, professional, and curious** tone in all responses.  
'''

novaPrompt = f'''
Search Query: {query_str}
Results Found: {result_found}
Number of Results: {numberOfResults}
'''

novaResponse = client.models.generate_content(
    model='gemini-2.0-flash',
    config=types.GenerateContentConfig(
        system_instruction=novaPersonality,
        temperature=2.0,
    ),
    contents=novaPrompt
)
print(novaResponse.text)
