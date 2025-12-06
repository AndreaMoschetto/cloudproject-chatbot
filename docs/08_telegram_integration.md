
# 8. Advanced Telegram Bot Integration

While the initial design envisioned the Telegram Bot merely as a file uploader, the final implementation evolved into a complete **Remote Command Center**. The bot now supports full interaction with the Knowledge Base (CRUD operations) and implements a security layer to prevent unauthorized access.

## 🛡️ Security: The Whitelist Mechanism

Since Telegram bots are publicly accessible by default, a "Soft Security" mechanism was implemented to prevent unauthorized users from uploading malicious files or deleting data.

### Logic
The Lambda function checks the sender's `chat_id` against a list of allowed IDs defined in the infrastructure variables.

1.  **Configuration:** Terraform injects an `ALLOWED_IDS` environment variable (comma-separated list) into the Lambda.
2.  **Enforcement:** Upon receiving a webhook, the Lambda compares the incoming `chat_id`.
3.  **User Experience:** If the user is unauthorized, the bot replies with an **Access Denied** message containing their `chat_id`. This allows the administrator to easily copy the ID and add it to the Terraform configuration if access needs to be granted.

```python
# Pseudo-code logic
if chat_id not in ALLOWED_IDS:
    return "⛔ Access Denied. Your ID is: 123456"
```

## 🎮 Command Features (Mini-CRUD)

The bot acts as a client for the Orchestrator's REST API, effectively bridging the chat interface with the backend services.

### 1. File Sanitization & Upload

When a PDF is sent:

  * **Sanitization:** The filename is processed to remove spaces and special characters (replaced by underscores) to prevent filesystem or URL encoding issues (e.g., `My Notes.pdf` -\> `My_Notes.pdf`).
  * **Metadata Tagging:** The file is uploaded to S3 with a specific metadata tag: `chat_id`. This allows the RAG Service to "callback" the specific user via Telegram once the asynchronous ingestion is complete.
  * **HTML Parsing:** Responses use HTML parsing mode to safely display filenames with underscores without breaking Telegram's formatting.

### 2. List Files (`/list`)

Allows the administrator to see the current state of the Knowledge Base.

  * **Flow:** Telegram -\> Lambda -\> `GET /files` (Orchestrator) -\> `GET /files` (RAG Service).
  * **Response:** Returns a formatted list of all PDF files currently stored in the RAG container's disk.

### 3. Delete Files (`/delete <filename>`)

Allows the removal of obsolete or erroneous documents.

  * **Flow:** Telegram -\> Lambda -\> `DELETE /files/{filename}` (Orchestrator).
  * **Dual Cleanup:** The system ensures consistency by performing a double deletion:
    1.  **Disk:** The physical PDF file is removed from the RAG container storage.
    2.  **Vector Store:** All vector embeddings associated with that specific file (`metadata['source'] == filename`) are purged from ChromaDB.

## 🧩 Architecture Update: Hybrid Communication

The Telegram integration introduces a hybrid communication pattern:

1.  **Asynchronous (Uploads):**

      * Files are not sent to the backend directly. They go to **S3**, triggering an event-driven chain. This ensures robustness for large files.

2.  **Synchronous (Commands):**

      * Commands like `/list` and `/delete` require immediate feedback. The Lambda makes direct synchronous HTTP calls to the **Orchestrator's public HTTPS endpoint**.

This dual approach ensures the system is responsive for management tasks while remaining resilient for heavy data processing.

---
<div align="center">

[← Previous Chapter](07_cicd_and_devops.md) | [🏠 Back to Home](../README.md) | [Next Chapter: API Reference →](09_api_reference.md)

</div>