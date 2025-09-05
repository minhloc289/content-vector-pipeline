# Article Scraper and OpenAI Vector Store Uploader

## About

This project aims to:

1. **Automatically scrape articles**.
2. **Convert HTML to Markdown** and store newly updated content or skip unchanged files.
3. **Upload Markdown files to OpenAI Vector Store** for AI assistant retrieval purposes.

## Project Structure

```plaintext
src/
├── main.py                 # Main orchestration script
├── scraper/                # Handles scraping & Markdown conversion
│   ├── fetcher.py          # Fetches articles
│   ├── converter.py        # Converts HTML to Markdown
│   └── scraper.py          # Main scraping logic
├── uploader/               # Handles OpenAI Vector Store interactions
│   ├── upload.py           # Uploads articles to OpenAI Vector Store
│   ├── vector_store.py     # Manages vector store operations
│   └── file_handlers.py    # Handles file operations
├── config.py               # Configuration file
├── requirements.txt        # Python dependencies
└── .env.example            # Example environment variables file
```

Additional files/directories:

- `articles_metadata.json`: Stores all article states, useful for delta detection
- `articles/`: Generated dynamically during execution

## Installation

### Clone the Repository

```bash
git clone https://github.com/minhloc289/alphasphere-assignment.git
cd alphasphere-assignment
```

## Running Locally

### Install Dependencies

#### Initialize a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # (Linux/macOS)
venv\Scripts\activate     # (Windows)
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Copy Environment Variables

```bash
cp .env.example .env
```

Replace the placeholder values in `.env` with your actual OpenAI API key and other necessary configurations.

#### Run the Script

```bash
python -m src.main
```

## Running with Docker

### Build Docker Image

```bash
docker build -t alphasphere-assignment:latest .
```

### Run Docker Container (with cron job)

```bash
docker run -e OPENAI_API_KEY="your_openai_api_key" --name your_container_name alphasphere-assignment:latest
```

### Run Script Once via Docker

```bash
docker run -e OPENAI_API_KEY="your_openai_api_key" --name your_container_name alphasphere-assignment:latest /usr/local/bin/python -m src.main
```

### View Docker Logs for Execution Output

```bash
docker logs your_container_name
```

## Chunking Strategy Explanation (Vector Store API)

In the `src/uploader/vector_store.py` module, the project uses a **static chunking strategy** for file uploads to OpenAI Vector Store.

### Code Snippet:

```python
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
```

### Why Static Chunking?

**Static chunking** helps produce predictable, uniform chunks. This is important for documentation-style Markdown files because:

- Each chunk cleanly captures a logical text unit (e.g., a section of content).
- Overlap ensures no semantic gap between chunks, preserving context.

### Parameter Choices:

| Parameter               | Value | Explanation                                                                      |
| ----------------------- | ----- | -------------------------------------------------------------------------------- |
| `max_chunk_size_tokens` | 600   | Each chunk maxes out at 600 tokens to balance context size vs. retrieval speed.  |
| `chunk_overlap_tokens`  | 200   | 200 tokens of overlap ensures boundary continuity, improving retrieval accuracy. |

## Assignment Report

1. **Assistant Playground Screenshot**

   Verifying retrieval works properly with uploaded vectors.

   ![OpenAI Playground Screenshot](https://github.com/minhloc289/alphasphere-assignment/blob/main/report/playground_screenshot.png?raw=true)

2. **Cron Job Logs**

   For the demo, I started the cron job to run every 10 minutes, capturing the output in `cron.log`. This log file contains details of each run, including counts of added, updated, and skipped articles. You can view more details here [Cron Log](https://github.com/minhloc289/alphasphere-assignment/blob/main/report/cron.log)

   For the final submission, I will set it to run daily, and the log will reflect that change.

   ```bash
   0 0 * * * cd /app && echo "----- START: Script execution at $(date) -----" >> /var/log/cron.log && /usr/local/bin/python -m src.main >> /var/log/cron.log 2>&1; echo "----- END: Script execution completed at $(date) with exit code $? -----" >> /var/log/cron.log
   ```

   Also you can see the container demonstrating the deployment and execution

   ![Container Screenshot](https://github.com/minhloc289/alphasphere-assignment/blob/main/report/container.png?raw=true)

3. **Video Demo**

   A recorded video walkthrough demonstrating the scraping, uploading, and retrieval processes successfully completed. You can see here [Demo Link](https://drive.google.com/drive/folders/101_OJofVqCUnaTtaz_MHyjNk9x_zbAE3?usp=sharing)
