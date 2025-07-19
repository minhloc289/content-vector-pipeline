import logging
from datetime import datetime
from .vector_store import ensure_vector_store_exists, upload_files_to_vector_store_batch
from .file_handlers import validate_article_file_paths 
from ..config import BATCH_SIZE, VECTOR_STORE_NAME, setup_logging

# Configure logging for the upload module
logger = setup_logging()

def upload_delta_articles_in_batches(categorized_articles, tracked_metadata, batch_size=BATCH_SIZE):
    """
    Upload new or updated articles to the vector store in batches based on categorized_articles.

    This function takes categorized_articles containing new and updated article IDs,
    constructs their Markdown file paths, and uploads them in batches of the specified size.

    Args:
        categorized_articles (dict): Dictionary with 'new_articles' and 'updated_articles' sets of article IDs.
        tracked_metadata (dict): Dictionary containing article_id -> metadata with 'title'.
        batch_size (int): Number of files to upload per batch. Defaults to 10.
    """
    start_time = datetime.now()
    logger.info(f"[Upload] Starting upload process at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    new_count = len(categorized_articles.get("new_articles", set()))
    updated_count = len(categorized_articles.get("updated_articles", set()))
    total_articles = new_count + updated_count
    
    logger.info(f"[Upload] Articles to process: {total_articles} total ({new_count} new, {updated_count} updated)")
    logger.info(f"[Upload] Batch size: {batch_size}")
    
    if total_articles == 0:
        logger.info("[Upload] No articles to upload")
        return
    
    try:
        # Ensure vector store exists
        logger.info("[Upload] Ensuring vector store exists...")
        vector_store_id = ensure_vector_store_exists(name=VECTOR_STORE_NAME)
        
        # Validate article file paths
        logger.info("[Upload] Validating article file paths...")
        valid_paths, missing_paths = validate_article_file_paths(categorized_articles, tracked_metadata)

        if missing_paths:
            logger.error(f"[Upload] {len(missing_paths)} article files are missing, upload cannot proceed")
            return

        if not valid_paths:
            logger.warning("[Upload] No valid article files found for upload")
            return

        logger.info(f"[Upload] Ready to upload {len(valid_paths)} valid article files")

        # Initialize counters
        total_files_embedded = 0
        total_chunks_embedded = 0
        successful_batches = 0
        failed_batches = 0
        total_batches = (len(valid_paths) + batch_size - 1) // batch_size

        logger.info(f"[Upload] Starting batch upload: {total_batches} batches planned")

        # Upload files in batches
        for batch_num in range(0, len(valid_paths), batch_size):
            batch_start_time = datetime.now()
            batch_paths = valid_paths[batch_num:batch_num + batch_size]
            current_batch_number = batch_num // batch_size + 1
            
            try:
                logger.info(f"[Upload] Processing batch {current_batch_number}/{total_batches} ({len(batch_paths)} files)")
                
                # Upload the current batch of files to the vector store
                file_batch = upload_files_to_vector_store_batch(batch_paths, vector_store_id)
                
                # Extract metrics
                current_files = len(batch_paths)
                current_chunks = 0
                if hasattr(file_batch, 'file_counts') and file_batch.file_counts:
                    current_chunks = getattr(file_batch.file_counts, 'completed', 0)
                
                # Update totals
                total_files_embedded += current_files
                total_chunks_embedded += current_chunks
                successful_batches += 1
                
                # Calculate batch time
                batch_end_time = datetime.now()
                batch_time = batch_end_time - batch_start_time
                
                logger.info(f"[Upload] Batch {current_batch_number} completed in {batch_time.total_seconds():.2f}s")
                logger.info(f"[Upload] Batch results: {current_files} files, {current_chunks} chunks processed")
                logger.debug(f"[Upload] Running totals: {total_files_embedded} files, {total_chunks_embedded} chunks")

            except Exception as e:
                failed_batches += 1
                batch_end_time = datetime.now()
                batch_time = batch_end_time - batch_start_time
                
                logger.error(f"[Upload] Batch {current_batch_number} failed after {batch_time.total_seconds():.2f}s: {e}")
                logger.error(f"[Upload] Failed batch contained {len(batch_paths)} files")

        # Calculate final execution time
        end_time = datetime.now()
        execution_time = end_time - start_time
        
        # Log final summary
        logger.info(f"[Upload] Upload process completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"[Upload] Total execution time: {execution_time.total_seconds():.2f} seconds")
        logger.info(f"[Upload] Batch summary: {successful_batches} successful, {failed_batches} failed")
        logger.info(f"[Upload] Final results: {total_files_embedded} files embedded, {total_chunks_embedded} chunks created")
        
        if failed_batches > 0:
            logger.warning(f"[Upload] {failed_batches} batches failed - some articles may not be available for search")
        else:
            logger.info("[Upload] All batches completed successfully")

    except Exception as e:
        end_time = datetime.now()
        execution_time = end_time - start_time
        logger.error(f"[Upload] Upload process failed after {execution_time.total_seconds():.2f} seconds: {e}")
        logger.error("[Upload] Vector store upload could not be completed")