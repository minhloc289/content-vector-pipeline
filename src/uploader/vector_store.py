from openai import OpenAI
from typing import List
from ..config import (
    OPENAI_API_KEY,
    MAX_CHUNK_SIZE_TOKENS,
    CHUNK_OVERLAP_TOKENS
)

client = OpenAI(api_key=OPENAI_API_KEY)

def get_vector_store_by_name(name="OptiBotVectorStore") -> str | None:
    """
    Retrieve the ID of a vector store by its name.

    Args:
        name (str): The name of the vector store to look for. Defaults to "OptiBotVectorStore".

    Returns:
        str | None: The ID of the existing vector store if found, otherwise None.
    """
    try: 
        # List all vector stores and check for the one with the given name
        vector_stores = client.vector_stores.list()
        for store in vector_stores.data:
            if store.name == name:
                return store.id
        return None
    except Exception as e:
        raise RuntimeError(f"Error retrieving vector store by name '{name}': {e}")

def create_vector_store(name="OptiBotVectorStore") -> str:
    """
    Create a new vector store with the given name and return its ID.

    Args:
        name (str): The name to assign to the new vector store. Defaults to "OptiBotVectorStore".

    Returns:
        str: The ID of the newly created vector store.
    """
    try:
        # Create a new vector store with the specified name
        store = client.vector_stores.create(name=name)
        print(f"Created Vector Store: {store.name} with ID: {store.id}")

        return store.id
    except Exception as e:
        raise RuntimeError(f"Error creating vector store: {e}")

def ensure_vector_store_exists(name="OptiBotVectorStore") -> str:
    """
    Ensure a vector store exists. If it exists, return its ID; if not, create it and return the new ID.

    Args:
        name (str): The name of the vector store to check or create. Defaults to "OptiBotVectorStore".

    Returns:
        str: The ID of the existing or newly created vector store.
    """
    # Check if the vector store already exists
    existing_id = get_vector_store_by_name(name)
    if existing_id:
        print(f"Ensure vector store exists: {name} - ID: {existing_id}")
        return existing_id

    # If not found, create a new vector store
    new_id = create_vector_store(name)
    print(f"Created new Vector Store: {name} - ID: {new_id}")
    return new_id

def upload_files_to_vector_store_batch(file_paths: List[str], vector_store_id: str):
    """
    Upload multiple files to a vector store in one batch.

    Args:
        file_paths (List[str]): List of file paths (.md).
        vector_store_id (str): Target Vector Store ID.

    Returns:
        None
    """
    try:
        # Ensure all file paths are valid
        file_streams = [open(path, "rb") for path in file_paths]

        # Upload files in batch
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=file_streams,
            chunking_strategy={
                "type": "static",
                "static": {
                    "max_chunk_size_tokens": MAX_CHUNK_SIZE_TOKENS,
                    "chunk_overlap_tokens": CHUNK_OVERLAP_TOKENS
                }
            }
        )

        print(f"Batch upload status: {file_batch.status}")
        print(f"File counts: {file_batch.file_counts}")

        return file_batch

    except Exception as e:
        print(f"Error during batch upload: {e}")
        raise
