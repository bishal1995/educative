import logging
import os
from mcp.server.fastmcp import FastMCP
from typing import List
from dotenv import load_dotenv 

#Langchain imports for RAG Pipiline
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from chromadb import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Load all API keys
load_dotenv()

# --- ChromaDB directory setup for RAG and text files containing the employee handbook ---
CHROMA_DB_DIR = "files/chroma_db"
EMPLOYEE_HANDBOOK_FILE_PATH = "files/employee_handbook.txt"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialise FastMCP Server
mcp = FastMCP("employee_mcp")

# Initialize the embedding model for generating vector embeddings of document chunks
embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

@mcp.tool()
def ingest_employee_handbook() -> str:
    """
    Loads a document from a file path, splits it into chunks, generates
    embeddings using Google's model, and stores them in a persistent
    Chroma vector store for later retrieval.

    This tool is the first step in the RAG pipeline. It prepares the knowledge
    base that can be queried by another tool.

    Args:
        file_path: The absolute or relative path to the text document.
                   For example: "/usercode/Guides/employee_handbook.txt".

    Returns:
        A string confirming the successful ingestion and the number of chunks processed,
        or an error message if the process fails.
    """
    file_path = f"{CURRENT_DIR}/{EMPLOYEE_HANDBOOK_FILE_PATH}"
    if not os.path.exists(file_path):
        return f"Error: The file path '{file_path}' does not exist."    
    else:
        try:
            # Load the document using TextLoader
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
            # Split the document into smaller chunks using RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            if not chunks:
                return "Error: No chunks were created from the document. Please check the file content and splitting parameters."
            # 5. Ingest the chunks into the Chroma vector store
            # The `from_documents` is configured to save the data to the specified persistent directory            
            vector_store = Chroma.from_documents(
                documents = chunks,
                embedding = embedding_model,
                persist_directory = f"{CURRENT_DIR}/{CHROMA_DB_DIR}",
                client_settings = Settings(anonymized_telemetry = False) # Disable telemetry for privacy
            )
            return f"Successfully ingested the employee handbook file : {file_path}. Total chunks created: {len(chunks)}."
        except Exception as e:
            print(f"An error occurred during ingestion: {str(e)}")
            return f"Error: An exception occurred during ingestion. Details: {str(e)}"
        
@mcp.tool()
def query_employee_handbook_vector_store(query: str) -> str:
    """
    Queries the persistent Chroma vector store to find the most relevant
    document chunks for a given user query.

    This tool loads the existing vector database, performs a similarity search,
    and returns the combined text of the most relevant chunks.

    Args:
        query: The user's question or search term (e.g., "how do I apply for leave?").

    Returns:
        A string containing the concatenated content of the most relevant document
        chunks, or an error/status message if no relevant information is found.
    """
    try:
        if not os.path.exists(f"{CURRENT_DIR}/{CHROMA_DB_DIR}"):
            return f"Error: The Chroma vector store directory '{CURRENT_DIR}/{CHROMA_DB_DIR}' does not exist. Please run the ingestion tool first."
        else:
            # Load the existing Chroma vector store
            logger.info(f"Loading Chroma vector store from directory: {CURRENT_DIR}/{CHROMA_DB_DIR}")
            vector_store = Chroma(
                persist_directory = f"{CURRENT_DIR}/{CHROMA_DB_DIR}",
                embedding_function = embedding_model,
                client_settings = Settings(anonymized_telemetry = False) # Disable telemetry for privacy
            )
            # Perform a similarity search to find the most relevant chunks
            result_chunks = vector_store.similarity_search(query, k=3) # Retrieve top 3 relevant chunks

            if not result_chunks:
                return "No relevant information found in the employee handbook for your query."
            else:
                query_results = "\n---\n".join([answer.page_content for answer in result_chunks])
                return query_results
    except Exception as e:
        print(f"An error occurred during querying: {str(e)}")
        return f"Error: An exception occurred during querying. Details: {str(e)}"
    
if __name__ == "__main__":
    logger.info("Starting the Employee MCP server...")
    mcp.run(transport = "stdio")
