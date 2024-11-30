# RAGForge

## Phidata RAG Application with Ollama Agent and Embedding

![Dashboard](https://pinsker.ai/web/image/1487-856033c6/dashboard.webp)

This application serves as a template for a completely local agentic Retrieval-Augmented Generation (RAG) setup with a clean web interface. It integrates vectorization capabilities using **PhiData** to organize and retrieve knowledge efficiently from various data sources. The application utilizes **Open Hermes** for retrieval and context refinement, and **Llama 3.2** for response generation, providing a robust framework for knowledge-driven conversational AI.

The application supports:

- Local folders
- Drag and drop files
- AWS S3
- Google Drive
- Confluence

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Model Workflow](#model-workflow)
- [Vectorization and Knowledge Base](#vectorization-and-knowledge-base)
- [Customization](#customization)
- [License](#license)
- [Additional Resources](#additional-resources)
- [Contributing](#contributing)

## Prerequisites

Before installing and running the application, ensure you have the following installed on your system:

- **[Git](https://git-scm.com/downloads)**
- **[Docker](https://docs.docker.com/engine/install/)**
- **[Docker Compose](https://docs.docker.com/compose/install/)**
- **[Ollama](https://ollama.com/download)**
- **Required Models**:
  - **Llama 3.2 Model**: Pull the model using Ollama with the command:

    ```bash
    ollama pull llama3.2
    ```

  - **OpenHermes Model**: Pull the `openhermes` model using Ollama with the command:

    ```bash
    ollama pull openhermes
    ```

## Installation

Follow these steps to install and run the application:

### 1. Clone the Repository

Clone the repository to your local machine using `git clone`:

```bash
git clone https://github.com/JuliusPinsker/RAGForge.git
```

### 2. Navigate to the Project Directory

Change your current directory to the cloned repository:

```bash
cd RAGForge
```

### 3. Build and Run the Docker Services

Use Docker Compose to build the Docker images and start the services in detached mode:

```bash
docker compose up --build -d
```

This command will:

- Clone the **PhiData** repository.
- Build the application image using the provided `Dockerfile`.
- Start the PostgreSQL database and the application services as defined in `docker-compose.yml`.

## Configuration

### Embedding Model

The embedding model used in this application can be specified in the `app.py` file within the `create_knowledge_base` function. The default embedding model is `llama3.2`, but the retrieval and response generation process leverages both `openhermes` and `llama3.2`:

- **Open Hermes** handles retrieval and context refinement from the knowledge base.
- **Llama 3.2** generates the final responses.

Ensure that both models are pulled using Ollama before running the application.

## Usage

Once the application is running, you can access the web interface at [http://localhost:8501](http://localhost:8501).

### Features

- **File Browsing**: Browse and select files from local directories to load into the knowledge base.
- **Drag and Drop**: Upload files directly through the web interface.
- **External Connections**: Connect and load files from AWS S3, Google Drive, and Confluence.

### Supported File Formats

- PDF (`.pdf`)
- Text files (`.txt`)
- Markdown files (`.md`)

### Chat Interface

- **Interact with the Agent**: Ask questions and receive responses based on the knowledge base.
- **Source Inclusion**: Responses include sources for better traceability.
- **Chat History**: View previous interactions for context.

---

## Model Workflow

This application employs **Open Hermes** and **Llama 3.2** in a collaborative workflow to enhance retrieval-augmented generation:

### Open Hermes: Retrieval and Context Building
- **Task**: Fetches relevant documents from the knowledge base.
- **Functionality**:
  - Performs similarity searches against the vector database.
  - Summarizes and refines retrieved content to provide the most relevant context for queries.
- **Specialty**: Ensures precise and domain-relevant information is selected for response generation.

### Llama 3.2: Response Generation
- **Task**: Generates conversational responses based on the context retrieved by Open Hermes.
- **Functionality**:
  - Processes retrieved context into natural language answers.
  - Ensures the responses are coherent, detailed, and user-friendly.
  - Incorporates sources into responses for traceability.

### Workflow Integration
1. **Query Interpretation**: The user’s query is passed to Open Hermes.
2. **Document Retrieval**: Open Hermes retrieves and refines relevant documents from the knowledge base.
3. **Response Generation**: Llama 3.2 generates the final response based on the retrieved context.

---

## Vectorization and Knowledge Base

### Vectorization Overview

This application employs vectorization to represent documents and text files as high-dimensional numerical embeddings using **PhiData**. These embeddings allow efficient semantic search and retrieval of relevant documents based on user queries.

### Components of Vectorization

1. **Vector Database**: 
   - Utilizes `pgvector`, a PostgreSQL extension for storing and querying vector embeddings.
   - Stores all document embeddings in a structured format for fast retrieval.

2. **Embedding Model**: 
   - Embeddings are generated using the `OllamaEmbedder` class from **PhiData**, which leverages state-of-the-art models like `llama3.2` and `openhermes`.

3. **Knowledge Base Integration**:
   - The application uses `AgentKnowledge`, a knowledge base class that connects to the vector database.
   - Handles the organization of embeddings, retrieval of documents, and inclusion of relevant sources in the responses.

---

## Customization

You can customize various settings through the web interface:

### Database Settings

- **Database URL**: Specify the database URL for the knowledge base.
- **Embeddings Table Name**: Define the table name where embeddings are stored.
- **Reload Knowledge Base**: Reload the knowledge base if changes are made.

### Connecting to External Services

#### AWS S3

- **Credentials**: Provide your AWS Access Key ID and Secret Access Key.
- **Bucket Name**: Specify the S3 bucket name to load files from.

#### Google Drive

- **Credentials JSON**: Paste your Google Drive service account credentials in JSON format.
- **File Loading**: Load supported files directly from your Google Drive.

#### Confluence

- **URL**: Enter your Confluence instance URL.
- **Username and API Token**: Provide your Confluence username and API token.
- **Content Loading**: Load attachments from Confluence pages.

---

## License

This project is licensed under the Mozilla Public License Version 2.0. See the [License](License.md) file for details.

## Additional Resources

To learn more about configuring the embedding model and other advanced features, please visit the [PhiData documentation on Ollama Embedder](https://docs.phidata.com/embedder/ollama).
