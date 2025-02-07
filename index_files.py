# index_files.py
import os
import sys
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID

# For PDF extraction
from pdfminer.high_level import extract_text

# For DOCX extraction
import docx


def get_docx_text(path):
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(path)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return "\n".join(fullText)
    except Exception as e:
        print(f"Error reading DOCX {path}: {e}")
        return ""


# --- Configuration ---
# Prompt for the directory to index. For safety, consider using a specific folder (e.g., Documents).
ROOT_DIR = '/Users/abhijnans/Documents/Knolwdge base Test'
if not os.path.isdir(ROOT_DIR):
    print("The provided path is not a valid directory.")
    sys.exit(1)

# Define the Whoosh schema
schema = Schema(
    file_path=ID(stored=True, unique=True),
    file_name=TEXT(stored=True),
    content=TEXT
)

# Create (or reuse) the index directory.
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

ix = create_in(index_dir, schema)
writer = ix.writer()

# Walk through the directory tree.
for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        content = ""
        ext = os.path.splitext(filename)[1].lower()

        # Handle PDF files
        if ext == ".pdf":
            try:
                content = extract_text(file_path)
            except Exception as e:
                print(
                    f"Skipping PDF file (error extracting text): {file_path} - {e}")
                continue

        # Handle DOCX files
        elif ext == ".docx":
            content = get_docx_text(file_path)
            if not content:
                print(f"Skipping DOCX file (no content): {file_path}")
                continue

        # Handle plain text files or others (try opening as UTF-8 text)
        else:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(
                    f"Skipping file (cannot read as text): {file_path} - {e}")
                continue

        # Optional: Skip very large files (e.g., > 10MB)
        if len(content) > 10 * 1024 * 1024:
            print(f"Skipping large file: {file_path}")
            continue

        # Add the document to the index if there is any content.
        if content.strip():
            writer.add_document(file_path=file_path,
                                file_name=filename, content=content)
            print(f"Indexed: {file_path}")
        else:
            print(f"No content extracted from: {file_path}")

writer.commit()
print("Indexing complete!")
