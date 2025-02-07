# search_files.py
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

# Open the index
ix = open_dir("indexdir")

# Set up a query parser for the 'content' field
parser = QueryParser("content", schema=ix.schema)

# Prompt the user for a query
query_str = input("Enter your search query: ").strip()

# Parse the query
query = parser.parse(query_str)

# Search the index and display results
with ix.searcher() as searcher:
    results = searcher.search(query, limit=20)  # Adjust limit as needed
    print(f"\nFound {len(results)} result(s):")
    for hit in results:
        print(f"File: {hit['file_name']}")
        print(f"Path: {hit['file_path']}\n")
