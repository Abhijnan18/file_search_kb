# search_files.py

import sys
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, AndGroup, OrGroup
from google import genai
from google.genai import types

# System instruction for keyword extraction
sys_instruct = (
    "You are a search query interpreter. Extract the essential search keywords from the following query "
    "and return only the keywords which will be most useful to search the file, separated by spaces."
)

# Initialize the GenAI client with your API key.
client = genai.Client(api_key='AIzaSyATzFXLi0fz4_1xXKMlpJAo760IBIVWWKo')

result_found = False

# Open the Whoosh index directory
ix = open_dir("indexdir")

# Prompt the user for a search query
query_str = input("Enter your search query: ")

# Generate keywords using the GenAI model.
response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=types.GenerateContentConfig(
        system_instruction=sys_instruct,
        temperature=0.0,
    ),
    contents=query_str
)

# Define a prompt to decide on the Boolean operator (AND vs OR)
andOrDeterminer = (
    "You will be provided with a natural language search query (string) and a set of keywords (space-separated string). "
    "Your task is to determine whether the keywords should be combined using the AND or OR operator when performing a search.\n"
    "1. If the search should use the AND operator, return 0.\n"
    "2. If the search should use the OR operator, return 1.\n"
    "3. If there is only one keyword, always return 1.\n"
    "You must return only a single digit (0 or 1) as output, without any explanations or additional text."
)

andOrDeterminerResponse = client.models.generate_content(
    model='gemini-2.0-flash',
    config=types.GenerateContentConfig(
        system_instruction=andOrDeterminer,
        temperature=0.0,
    ),
    contents=f"Search Query: {query_str}\nKeywords: {response.text}"
)

# Debug prints to check model outputs
print("Extracted Keywords:", response.text)
print("AND/OR Determiner Output:", andOrDeterminerResponse.text)

# Use .strip() to remove extra whitespace; if the output is "0", use AND grouping; otherwise, use OR grouping.
if andOrDeterminerResponse.text.strip() == "0":
    queryType = AndGroup
else:
    queryType = OrGroup

# Set up a MultifieldParser for both 'file_name' and 'content' fields.
# Boost the 'file_name' field by 2.0 so that matches in file names have higher weight.
fields = ["file_name", "content"]
fieldboosts = {"file_name": 2.0, "content": 1.0}
parser = MultifieldParser(fields, schema=ix.schema,
                          group=queryType, fieldboosts=fieldboosts)

# Parse the extracted keywords (trimmed) to construct a structured query.
query = parser.parse(response.text.strip())

print("Structured Query:", query)

# Search the index and display results.
with ix.searcher() as searcher:
    # limit results to 20 for brevity
    results = searcher.search(query, limit=20)
    numberOfResults = len(results)
    print(f"\nFound {numberOfResults} result(s):")
    if numberOfResults > 0:
        result_found = True
    for hit in results:
        print(f"File: {hit['file_name']}")
        print(f"Path: {hit['file_path']}\n")

# Define the Nova personality for generating a friendly response.
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
