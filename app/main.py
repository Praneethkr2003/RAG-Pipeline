import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional, Generator
import uvicorn
from pathlib import Path
from datetime import datetime
import json
import tempfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import database and other components
from .database import SessionLocal, engine, get_db, create_tables
from .json_processor import JSONProcessor
from .query_processor import QueryProcessor

# Initialize FastAPI app
app = FastAPI(
    title="JSON RAG Chatbot",
    description="Main application serving both the API and the frontend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize API router
api_router = APIRouter(
    prefix="/api",
    tags=["api"],
)

# Create database tables (only in non-serverless environment)
if not os.getenv("VERCEL"):
    create_tables()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File upload directory - use /tmp for Vercel compatibility
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize JSON processor with smaller chunk size for serverless
CHUNK_SIZE = 100  # Smaller chunks for serverless environments
json_processor = JSONProcessor(chunk_size=CHUNK_SIZE)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database sessions for each request"""
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

@api_router.post("/upload/", response_model=Dict[str, Any])
async def upload_file(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """
    Upload and process a JSON file
    
    The file will be processed in a streaming fashion to handle large files efficiently.
    """
    try:
        logger.info(f"Starting file upload processing for {file.filename}")
        # Validate file type
        if not file.filename.lower().endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JSON files are supported"
            )
        
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process the JSON file and save chunks to database
        from .database import JSONChunk
        import uuid
        
        chunks = []
        for chunk_type, chunk_data in json_processor.stream_json_file(file_path):
            # Generate unique chunk ID
            chunk_id = str(uuid.uuid4())
            
            # Extract metadata
            metadata = json_processor.extract_metadata(chunk_data, chunk_type)
            
            # Create database record
            db_chunk = JSONChunk(
                chunk_id=chunk_id,
                source_file=file.filename,
                chunk_type=chunk_type,
                metadata_=metadata,
                content=chunk_data  # Store the actual patient data
            )
            
            # Save to database
            db.add(db_chunk)
            db.commit()
            
            chunks.append({
                'chunk_id': chunk_id,
                'chunk_type': chunk_type,
                'item_count': len(chunk_data) if isinstance(chunk_data, list) else 1,
                'metadata': metadata
            })
        
        logger.info(f"Successfully processed file {file.filename}")
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_processed": len(chunks),
            "chunks": chunks
        }
        
    except Exception as e:
        logger.exception("An error occurred during file upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up the uploaded file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

@api_router.post("/query/", response_model=Dict[str, Any])
async def process_query(
    query: Dict[str, str],
    db = Depends(get_db)
):
    """
    Process a natural language query against the stored data
    
    The system will first attempt to answer the query using direct database lookups.
    If the query is too complex, it will use a language model to generate a response.
    """
    if 'query' not in query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter is required"
        )
    
    try:
        # Initialize query processor with database session
        processor = QueryProcessor(db)
        
        # Process the query
        result = processor.process_query(query['query'])
        
        return {
            "query": query['query'],
            "response": result['response'],
            "is_direct": result.get('is_direct', False),
            "metadata": result.get('metadata', {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@api_router.post("/chat/")
async def chat_endpoint(
    request: Request,
    db = Depends(get_db)
):
    """
    Handle chat requests from the UI with streaming support
    """
    try:
        data = await request.json()
        messages = data.get('messages', [])
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Messages array is required"
            )
        
        # Get the last user message
        last_message = next((msg for msg in reversed(messages) if msg['role'] == 'user'), None)
        if not last_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user message found in the conversation"
            )
        
        # Initialize query processor
        processor = QueryProcessor(db)
        
        # Process the query (use the last user message as the query)
        result = processor.process_query(last_message['content'])
        
        # For streaming response
        async def generate():
            # In a real implementation, you would stream the response
            # For simplicity, we'll just return the full response
            yield f"data: {json.dumps({'content': result['response']})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("VERCEL_ENV", "development"),
        "region": os.getenv("VERCEL_REGION", "local")
    }

# Include the API router in the main app
app.include_router(api_router)

# Mount the static files directory for the frontend
# This assumes the Next.js frontend is built into the 'rag-chatbot-ui/out' directory
static_files_path = Path(__file__).resolve().parent.parent / "rag-chatbot-ui" / "out"
if not static_files_path.exists():
    static_files_path.mkdir(parents=True, exist_ok=True)
    print(f"Created static directory at: {static_files_path}")

app.mount("/", StaticFiles(directory=str(static_files_path), html=True), name="static")

# This is required for Vercel to discover the app
app = app

# Only run with uvicorn in local development
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")), 
        reload=True
    )
