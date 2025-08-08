# JSON RAG Chatbot

A cost-optimized Retrieval-Augmented Generation (RAG) chatbot for querying large JSON files (up to 1 billion parameters) with minimal compute requirements.

## Features

- **Streaming JSON Parser**: Handles large JSON files without loading them entirely into memory
- **Hybrid Query Processing**: Combines direct database queries with language model capabilities
- **Cost-Effective**: Minimizes compute costs by using database operations for simple queries
- **Scalable**: Designed to handle very large datasets efficiently
- **Easy Integration**: Simple REST API for uploading files and querying data

## Architecture

The system is built with the following components:

1. **FastAPI Backend**: Handles file uploads and query processing
2. **PostgreSQL with JSONB**: Stores and indexes JSON chunks for efficient querying
3. **Streaming JSON Parser**: Processes large JSON files in chunks
4. **Hybrid Query Processor**: Routes queries to either direct database lookups or language models
5. **OpenAI Integration**: For handling complex natural language queries

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API key (for complex queries)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd json-rag-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/json_rag_db
   GEMINI_API_KEY=your_gemini_api_key
   ```
   
   To get a Gemini API key:
   1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   2. Sign in with your Google account
   3. Click "Create API Key"
   4. Copy the API key and add it to your `.env` file

5. Initialize the database:
   ```bash
   python -c "from app.database import create_tables; create_tables()"
   ```

## Usage

1. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Upload a JSON file:
   ```bash
   curl -X POST "http://localhost:8000/upload/" \
        -H "accept: application/json" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@path/to/your/file.json"
   ```

3. Query the data:
   ```bash
   curl -X POST "http://localhost:8000/query/" \
        -H "Content-Type: application/json" \
        -d '{"query": "What was the average glucose level on May 2, 2025?"}'
   ```

## API Endpoints

- `POST /upload/`: Upload and process a JSON file
- `POST /query/`: Submit a natural language query
- `GET /health`: Health check endpoint

## Performance Considerations

- **Memory Efficiency**: The system uses streaming JSON parsing to handle files much larger than available RAM
- **Query Optimization**: Direct database queries are used for simple lookups to minimize costs
- **Batch Processing**: Large files are processed in chunks to maintain responsiveness
- **Caching**: Consider implementing caching for frequently accessed data

## Vercel Deployment

This application can be easily deployed to Vercel. Follow these steps:

1. **Prerequisites**:
   - A Vercel account
   - A PostgreSQL database (you can use Supabase, Neon, or any other PostgreSQL provider)
   - Gemini API key

2. **Deployment Steps**:

   a. **Fork and Clone** the repository
   
   b. **Install Vercel CLI** (if deploying locally):
      ```bash
      npm install -g vercel
      ```
   
   c. **Set up environment variables** in Vercel:
      - `DATABASE_URL`: Your PostgreSQL connection string
      - `GEMINI_API_KEY`: Your Google Gemini API key
      - `UPLOAD_DIR`: Set to `/tmp` (Vercel's writable directory)
   
   d. **Deploy using Vercel CLI**:
      ```bash
      vercel login
      vercel link
      vercel
      ```
   
   Or deploy directly from GitHub by importing the repository in the Vercel dashboard.

3. **Important Notes for Vercel**:
   - The free tier has a 10s timeout for serverless functions
   - File uploads are stored in `/tmp` which is ephemeral
   - Consider using external storage (like S3) for file persistence
   - Database connections should use connection pooling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Uses [PostgreSQL](https://www.postgresql.org/) for efficient JSON storage and querying
- Integrates with [Google's Gemini](https://ai.google.dev/) for natural language understanding
- Deployed on [Vercel](https://vercel.com/)
