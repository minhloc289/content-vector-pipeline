import logging
from datetime import datetime
from openai import OpenAI
from typing import List
from ..config import (
    OPENAI_API_KEY,
    MAX_CHUNK_SIZE_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    VECTOR_STORE_NAME,
    setup_logging
)

# Configure logging for the vector store module
logger = setup_logging()

client = OpenAI(api_key=OPENAI_API_KEY)

def get_vector_store_by_name(name) -> str | None:
    """
    Retrieve the ID of a vector store by its name.

    Args:
        name (str): The name of the vector store to look for. Defaults to "OptiBotVectorStore".

    Returns:
        str | None: The ID of the existing vector store if found, otherwise None.
    """
    try: 
        logger.debug(f"[VectorStore] Searching for vector store: '{name}'")
        
        # List all vector stores and check for the one with the given name
        vector_stores = client.vector_stores.list()
        logger.debug(f"[VectorStore] Found {len(vector_stores.data)} existing vector stores")
        
        for store in vector_stores.data:
            if store.name == name:
                logger.debug(f"[VectorStore] Found existing vector store: '{name}' (ID: {store.id})")
                return store.id
                
        logger.debug(f"[VectorStore] Vector store '{name}' not found")
        return None
        
    except Exception as e:
        logger.error(f"[VectorStore] Failed to retrieve vector store '{name}': {e}")
        raise RuntimeError(f"Error retrieving vector store by name '{name}': {e}")

def create_vector_store(name) -> str:
    """
    Create a new vector store with the given name and return its ID.

    Args:
        name (str): The name to assign to the new vector store. Defaults to "OptiBotVectorStore".

    Returns:
        str: The ID of the newly created vector store.
    """
    try:
        logger.info(f"[VectorStore] Creating new vector store: '{name}'")
        
        # Create a new vector store with the specified name
        store = client.vector_stores.create(name=name)
        logger.info(f"[VectorStore] Successfully created vector store: '{name}' (ID: {store.id})")

        return store.id
        
    except Exception as e:
        logger.error(f"[VectorStore] Failed to create vector store '{name}': {e}")
        raise RuntimeError(f"Error creating vector store: {e}")

def ensure_vector_store_exists(name=VECTOR_STORE_NAME) -> str:
    """
    Ensure a vector store exists. If it exists, return its ID; if not, create it and return the new ID.

    Args:
        name (str): The name of the vector store to check or create. Defaults to "OptiBotVectorStore".

    Returns:
        str: The ID of the existing or newly created vector store.
    """
    logger.debug(f"[VectorStore] Ensuring vector store exists: '{name}'")
    
    # Check if the vector store already exists
    existing_id = get_vector_store_by_name(name)
    if existing_id:
        logger.info(f"[VectorStore] Using existing vector store: '{name}' (ID: {existing_id})")
        return existing_id

    # If not found, create a new vector store
    new_id = create_vector_store(name)
    logger.info(f"[VectorStore] Vector store ready: '{name}' (ID: {new_id})")
    return new_id

def upload_files_to_vector_store_batch(file_paths: List[str], vector_store_id: str):
    """
    Upload multiple files to a vector store in one batch.

    Args:
        file_paths (List[str]): List of file paths (.md).
        vector_store_id (str): Target Vector Store ID.

    Returns:
        file_batch: The batch upload result object.
    """
    start_time = datetime.now()
    logger.debug(f"[VectorStore] Starting batch upload of {len(file_paths)} files")
    logger.debug(f"[VectorStore] Target vector store ID: {vector_store_id}")
    logger.debug(f"[VectorStore] Chunking config: {MAX_CHUNK_SIZE_TOKENS} tokens max, {CHUNK_OVERLAP_TOKENS} overlap")
    
    try:
        # Ensure all file paths are valid
        file_streams = []
        for path in file_paths:
            try:
                file_streams.append(open(path, "rb"))
            except Exception as e:
                logger.error(f"[VectorStore] Failed to open file {path}: {e}")
                raise

        logger.debug(f"[VectorStore] Successfully opened {len(file_streams)} files for upload")

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

        # Calculate execution time
        end_time = datetime.now()
        execution_time = end_time - start_time
        
        # Log results
        logger.info(f"[VectorStore] Batch upload completed in {execution_time.total_seconds():.2f} seconds")
        logger.info(f"[VectorStore] Upload status: {file_batch.status}")
        
        if hasattr(file_batch, 'file_counts') and file_batch.file_counts:
            completed = getattr(file_batch.file_counts, 'completed', 0)
            failed = getattr(file_batch.file_counts, 'failed', 0)
            in_progress = getattr(file_batch.file_counts, 'in_progress', 0)
            total = getattr(file_batch.file_counts, 'total', 0)
            
            logger.info(f"[VectorStore] File processing: {completed} completed, {failed} failed, {in_progress} in progress, {total} total")
            
            if failed > 0:
                logger.warning(f"[VectorStore] {failed} files failed to process")
        
        # Close file streams
        for stream in file_streams:
            stream.close()
            
        return file_batch

    except Exception as e:
        # Close file streams in case of error
        for stream in file_streams:
            try:
                stream.close()
            except:
                pass
                
        end_time = datetime.now()
        execution_time = end_time - start_time
        logger.error(f"[VectorStore] Batch upload failed after {execution_time.total_seconds():.2f} seconds: {e}")
        raise