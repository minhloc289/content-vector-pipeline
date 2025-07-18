from .vector_store import ensure_vector_store_exists, upload_files_to_vector_store_batch
from .file_handlers import validate_article_file_paths 
from ..config import BATCH_SIZE

def upload_delta_articles_in_batches(categorized_articles, batch_size=BATCH_SIZE):
    """
    Upload new or updated articles to the vector store in batches based on categorized_articles.

    This function takes categorized_articles containing new and updated article IDs,
    constructs their Markdown file paths, and uploads them in batches of the specified size.

    Args:
        categorized_articles (dict): Dictionary with 'newArticles' and 'updatedArticles' sets of article IDs.
        batch_size (int): Number of files to upload per batch. Defaults to 10.
    """
    try:
        # Ensure vector store exists
        vector_store_id = ensure_vector_store_exists(name="OptiBotVectorStore")
        
        # Validate article file paths
        valid_paths, missing_paths = validate_article_file_paths(categorized_articles)

        # Initialize upload process
        print(f"Starting upload of {len(valid_paths)} valid article files to vector store {vector_store_id}")
        print(f"Missing article files: {len(missing_paths)}")

        # Initialize counters
        total_files_embedded = 0
        total_chunks_embedded = 0

        # Upload files in batches
        print(f"Starting batch upload process with {len(valid_paths)} files...")
        for batch_num in range(0, len(valid_paths), batch_size):
            try:
                # Get the current batch of file paths
                batch_paths = valid_paths[batch_num:batch_num + batch_size]
                batch_number = batch_num // batch_size + 1

                print(f"Uploading batch {batch_number} with {len(batch_paths)} files: {batch_paths}")
                
                # Upload the current batch of files to the vector store
                file_batch = upload_files_to_vector_store_batch(batch_paths, vector_store_id)
                current_files = len(batch_paths)
                current_chunks = file_batch.file_counts.completed if hasattr(file_batch.file_counts, "completed") else 0
                
                # Log the results
                total_files_embedded += current_files
                total_chunks_embedded += current_chunks
                print(f"Batch {batch_number} uploaded. Files: {current_files}, Chunks: {current_chunks}")
                print(f"Running totals - Files Embedded: {total_files_embedded}, Chunks Embedded: {total_chunks_embedded}")

            except Exception as e:
                print(f"Failed to upload batch {batch_num // batch_size + 1}. Error: {e}")
                print(f"Skipped files in batch: {batch_paths}")

        print(f"Completed uploading {total_files_embedded} articles to vector store")
        print(f"Total Files Embedded: {total_files_embedded}, Total Chunks Embedded: {total_chunks_embedded}")

    except Exception as e:
        print(f"Failed to complete batch upload process: {e}")
        

