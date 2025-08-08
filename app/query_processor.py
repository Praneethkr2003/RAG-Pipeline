from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, String
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()





class QueryProcessor:
    """Processes user queries and routes them to appropriate handlers"""
    
    def __init__(self, db: Session):
        """
        Initialize the query processor
        
        Args:
            db: Database session
        """
        self.db = db
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.direct_query_handlers = {
            'date_query': self._handle_date_query,
            'aggregate_query': self._handle_aggregate_query,
            'simple_lookup': self._handle_simple_lookup
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query and return a response
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary containing the response and metadata
        """
        # First, try to handle as a direct query
        direct_result = self._try_direct_query(query)
        if direct_result['is_direct']:
            return {
                'response': direct_result['response'],
                'is_direct': True,
                'metadata': direct_result.get('metadata', {})
            }
        
        # If not a direct query, use language model
        return self._handle_complex_query(query)
    
    def _try_direct_query(self, query: str) -> Dict[str, Any]:
        """
        Attempt to handle the query with direct database operations
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with 'is_direct' flag and response if successful
        """
        # Try to extract date information
        date_match = self._extract_date_info(query)
        if date_match:
            date_field, date_value = date_match
            return self._handle_date_query(query, date_field, date_value)
        
        # Try to handle as an aggregate query
        if any(word in query.lower() for word in ['average', 'total', 'sum', 'count', 'minimum', 'maximum']):
            return self._handle_aggregate_query(query)
        
        # Try simple lookup
        return self._handle_simple_lookup(query)
    
    def _extract_date_info(self, query: str) -> Optional[Tuple[str, str]]:
        """
        Extract date information from the query
        
        Args:
            query: User's query
            
        Returns:
            Tuple of (date_field, date_value) if found, else None
        """
        # Simple date pattern matching (can be enhanced with more sophisticated NLP)
        date_patterns = [
            (r'(?:on|for|date|day of)\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,\s*\d{4})?)', 'date'),
            (r'(?:on|for|date|day of)\s+(\d{4}-\d{2}-\d{2})', 'date'),
            (r'(?:last|past|previous)\s+(\d+)\s+(day|week|month|year)s?', 'relative_date'),
            (r'today', 'today'),
            (r'yesterday', 'yesterday'),
            (r'this (week|month|year)', 'this_period'),
            (r'last (week|month|year)', 'last_period')
        ]
        
        for pattern, date_type in date_patterns:
            match = re.search(pattern, query.lower())
            if match:
                if date_type == 'relative_date':
                    amount = int(match.group(1))
                    unit = match.group(2)
                    return self._calculate_relative_date(amount, unit)
                elif date_type == 'today':
                    return 'date', datetime.now().strftime('%Y-%m-%d')
                elif date_type == 'yesterday':
                    return 'date', (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                elif date_type == 'this_period':
                    unit = match.group(1)
                    return self._get_period_range(unit, 'this')
                elif date_type == 'last_period':
                    unit = match.group(1)
                    return self._get_period_range(unit, 'last')
                else:
                    return 'date', match.group(1)
        
        return None
    
    def _calculate_relative_date(self, amount: int, unit: str) -> Tuple[str, str]:
        """Calculate relative date based on amount and unit"""
        now = datetime.now()
        if unit.startswith('day'):
            target_date = now - timedelta(days=amount)
            return 'date', target_date.strftime('%Y-%m-%d')
        elif unit.startswith('week'):
            target_date = now - timedelta(weeks=amount)
            return 'date', target_date.strftime('%Y-%m-%d')
        elif unit.startswith('month'):
            # Approximate month as 30 days
            target_date = now - timedelta(days=30 * amount)
            return 'date', target_date.strftime('%Y-%m-%d')
        elif unit.startswith('year'):
            # Approximate year as 365 days
            target_date = now - timedelta(days=365 * amount)
            return 'date', target_date.strftime('%Y-%m-%d')
        
        return 'date', now.strftime('%Y-%m-%d')
    
    def _get_period_range(self, unit: str, period: str) -> Tuple[str, Dict[str, str]]:
        """Get date range for this/last period"""
        now = datetime.now()
        
        if unit == 'week':
            if period == 'this':
                start = now - timedelta(days=now.weekday())
                end = start + timedelta(days=6)
            else:  # last
                start = now - timedelta(days=now.weekday() + 7)
                end = start + timedelta(days=6)
        
        elif unit == 'month':
            if period == 'this':
                start = now.replace(day=1)
                next_month = now.replace(day=28) + timedelta(days=4)
                end = (next_month - timedelta(days=next_month.day)).replace(day=1) - timedelta(days=1)
            else:  # last
                first_day = now.replace(day=1)
                end = first_day - timedelta(days=1)
                start = end.replace(day=1)
        
        elif unit == 'year':
            if period == 'this':
                start = now.replace(month=1, day=1)
                end = now.replace(month=12, day=31)
            else:  # last
                start = now.replace(year=now.year-1, month=1, day=1)
                end = now.replace(year=now.year-1, month=12, day=31)
        
        return 'date_range', {
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d')
        }
    
    def _handle_date_query(self, query: str, date_field: str, date_value: any) -> Dict[str, Any]:
        """Handle queries with date filters by querying the database."""
        from .database import JSONChunk

        results = []
        try:
            if date_field == 'date':
                # Use the ->> operator to extract date fields as text for comparison
                results = self.db.query(JSONChunk).filter(
                    or_(
                        JSONChunk.metadata_.op('->>')('created_at').like(f"{date_value}%"),
                        JSONChunk.metadata_.op('->>')('date').like(f"{date_value}%")
                    )
                ).limit(10).all()
            elif date_field == 'date_range' and isinstance(date_value, dict):
                start_date = date_value.get('start')
                end_date = date_value.get('end')
                if start_date and end_date:
                    results = self.db.query(JSONChunk).filter(
                        or_(
                            JSONChunk.metadata_.op('->>')('created_at').between(start_date, end_date),
                            JSONChunk.metadata_.op('->>')('date').between(start_date, end_date)
                        )
                    ).limit(10).all()
        except Exception:
            # If the query fails (e.g., key doesn't exist), fall back to complex query handler
            pass

        if not results:
            return {'is_direct': False, 'response': None}

        response_text = f"Found {len(results)} records for the period {date_value}."
        sample_content = [res.content for res in results[:2]]

        return {
            'is_direct': True,
            'response': response_text,
            'metadata': {
                'query_type': 'date_query',
                'date_field': date_field,
                'date_value': date_value,
                'results_count': len(results),
                'sample_content': sample_content
            }
        }
    
    def _handle_aggregate_query(self, query: str) -> Dict[str, Any]:
        """
        Handle aggregate queries (sum, average, count, etc.).
        Currently, this falls back to the complex query handler.
        """
        # For now, we let the language model handle all aggregations.
        # A more advanced implementation could parse the query and build a SQL query.
        return {
            'is_direct': False,
            'response': None
        }
    
    def _handle_simple_lookup(self, query: str) -> Dict[str, Any]:
        """Handle simple lookup queries"""
        # This is a simplified example - actual implementation would query the database
        return {
            'is_direct': False,
            'response': None
        }
    
    def _handle_complex_query(self, query: str) -> Dict[str, Any]:
        """
        Handle complex queries using the Perplexity API.

        Args:
            query: User's natural language query.

        Returns:
            Dictionary containing the response from the language model.
        """
        try:
            relevant_chunks = self._retrieve_relevant_chunks(query)
            system_prompt, user_prompt = self._prepare_context_for_openai(relevant_chunks, query)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            return {
                'response': response.choices[0].message.content.strip(),
                'is_direct': False,
                'metadata': {
                    'model': 'gpt-3.5-turbo',
                }
            }

        except Exception as e:
            return {
                'response': f"Error processing your query with OpenAI: {str(e)}",
                'is_direct': False,
                'error': str(e)
            }
    
    def _retrieve_relevant_chunks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from the database based on the query.
        This implementation performs a simple keyword search.
        """
        from .database import JSONChunk  # Import here to avoid circular dependency issues

        keywords = [f"%{keyword.strip()}%" for keyword in query.lower().split() if len(keyword.strip()) > 2]
        if not keywords:
            return []

        # Build a query that searches for keywords in both metadata and content
        # Note: This uses string casting for JSONB fields, which is not highly performant
        # for large datasets. A full-text search index would be better.
        # Use the ->> operator to extract JSON fields as text for searching
        filters = [
            or_(
                JSONChunk.metadata_.op('->>')('search_text').ilike(kw),
                JSONChunk.content.op('->>')('text').ilike(kw),
                JSONChunk.content.cast(String).ilike(kw) # Fallback for unstructured content
            )
            for kw in keywords
        ]
        
        # Combine filters with OR logic
        combined_filter = or_(*filters)

        # Execute the query
        results = self.db.query(JSONChunk).filter(combined_filter).limit(limit).all()

        # Format results
        return [
            {
                'id': chunk.chunk_id,
                'content': chunk.content,
                'metadata': chunk.metadata_
            }
            for chunk in results
        ]
    
    def _prepare_context_for_openai(self, chunks: List[Dict[str, Any]], query: str) -> Tuple[str, str]:
        """
        Prepare system and user prompts for the OpenAI API.

        Args:
            chunks: List of relevant chunks.
            query: User's query.

        Returns:
            A tuple containing the system prompt and the user prompt.
        """
        system_prompt = """You are a helpful assistant that answers questions based on the provided data.
        Use the following pieces of context to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer."""

        user_prompt_context = "Context:\n"
        for i, chunk in enumerate(chunks, 1):
            chunk_str = json.dumps(chunk['content'], indent=2) if isinstance(chunk['content'], (dict, list)) else str(chunk['content'])
            user_prompt_context += f"--- Chunk {i} (Source: {chunk['metadata'].get('source', 'unknown')}, Type: {chunk['metadata'].get('type', 'unknown')}) ---\n{chunk_str}\n"

        user_prompt = f"{user_prompt_context}\nQuestion: {query}"

        return system_prompt, user_prompt
