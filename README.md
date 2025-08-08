# JSON RAG Chatbot

# Cost-Optimized RAG Chatbot for Large-Scale JSON Analysis

This project provides a high-performance, cost-optimized Retrieval-Augmented Generation (RAG) chatbot engineered to handle and query massive JSON datasets, scalable up to 1 billion entries or more. By leveraging a sophisticated hybrid query processing system, it intelligently routes user requests to either direct database lookups for factual data retrieval or to powerful Large Language Models (LLMs) for complex, inferential questions. This approach minimizes computational overhead and API costs while delivering fast, accurate responses.

## Key Features

- **Scalability for Massive Datasets**: Architected to handle JSON files with up to 1 billion parameters or entries, using a streaming parser that processes data in chunks without loading the entire file into memory.
- **Hybrid Query Processing**: A smart query router analyzes incoming questions. Simple, fact-based queries are translated into direct database lookups, while complex, contextual queries are sent to an LLM. This drastically reduces reliance on expensive LLM APIs.
- **Cost-Effective**: By minimizing LLM interactions, the system significantly lowers operational costs, making large-scale data analysis more accessible.
- **High Performance**: Direct database queries for simple questions are exceptionally fast, providing users with instant answers for a large class of inquiries.

## Architecture

The application is composed of two main parts:

- **Backend**: A Python-based backend built with **FastAPI** that handles file processing, RAG, and communication with a large language model (LLM).
- **Frontend**: A modern, responsive user interface built with **Next.js** and **React**.

### Backend (`app` directory)

- `main.py`: The main entry point of the FastAPI application. It defines all the API endpoints, including file upload and chat.
- `query_processor.py`: Contains the core logic for the RAG system. It processes user queries, retrieves relevant information from the vector store, and generates responses using the LLM.
- `json_processor.py`: Handles the parsing and chunking of uploaded JSON files before they are embedded and stored.
- `database.py`: Manages the connection to the vector database where the file embeddings are stored.

### Frontend (`rag-chatbot-ui` directory)

- `app/page.tsx`: The primary component for the chat interface.
- `components/`: A collection of reusable React components used to build the UI.
- `package.json`: Lists all the frontend dependencies and scripts.

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm (or pnpm/yarn)

### Backend Setup

1.  **Navigate to the project root directory.**
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create a `.env` file** in the root directory and add your API keys and other environment variables:
    ```
    OPENAI_API_KEY="your-openai-api-key"
    ```
5.  **Run the backend server:**
    ```bash
    uvicorn app.main:app --reload
    ```

### Frontend Setup

1.  **Navigate to the `rag-chatbot-ui` directory:**
    ```bash
    cd rag-chatbot-ui
    ```
2.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```
3.  **Create a `.env.local` file** in the `rag-chatbot-ui` directory and add the backend API URL:
    ```
    NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"
    ```
4.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```

## Deployment

The project is configured for deployment on **Vercel**. The `vercel.json` file and the `vercel_build.sh` script handle the deployment process. When deploying, ensure that all necessary environment variables are set in the Vercel project settings.
