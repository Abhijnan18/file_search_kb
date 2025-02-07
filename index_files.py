# index_files.py
import os
import sys
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from pdfminer.high_level import extract_text
import docx
from whoosh.analysis import RegexTokenizer, LowercaseFilter

# Define a custom analyzer for file names: split on underscores and non-alphabetic characters.
file_name_analyzer = RegexTokenizer(r"[A-Za-z0-9]+") | LowercaseFilter()

# Define the Whoosh schema with a custom analyzer for file_name.
schema = Schema(
    file_path=ID(stored=True, unique=True),
    file_name=TEXT(stored=True, analyzer=file_name_analyzer),
    content=TEXT
)

# Prompt for the directory to index.
ROOT_DIR = '/Users/abhijnans/Documents/Knolwdge base Test'
if not os.path.isdir(ROOT_DIR):
    print("The provided path is not a valid directory.")
    sys.exit(1)

# Create the index directory.
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

# Create the index.
ix = create_in(index_dir, schema)
writer = ix.writer()


def get_docx_text(path):
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX {path}: {e}")
        return ""


# Define allowed file extensions.
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Recursively walk through the directory tree.
for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
    for filename in filenames:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue  # Skip files that are not PDF, DOCX, or TXT.

        file_path = os.path.join(dirpath, filename)
        content = ""

        if ext == ".pdf":
            try:
                content = extract_text(file_path)
            except Exception as e:
                print(f"Skipping PDF file: {file_path} - {e}")
                continue
        elif ext == ".docx":
            content = get_docx_text(file_path)
            if not content:
                print(f"Skipping DOCX file (no content): {file_path}")
                continue
        elif ext == ".txt":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Skipping TXT file: {file_path} - {e}")
                continue

        # Optional: Skip very large files (over 10MB)
        if len(content) > 10 * 1024 * 1024:
            print(f"Skipping large file: {file_path}")
            continue

        # Add document to the index if there is content.
        if content.strip():
            writer.add_document(file_path=file_path,
                                file_name=filename, content=content)
            print(f"Indexed: {file_path}")
        else:
            print(f"No content extracted from: {file_path}")

writer.commit()
print("Indexing complete!")
