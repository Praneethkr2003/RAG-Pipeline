import ijson
import json
import os
import re
from typing import Dict, List, Any, Optional, Generator, Tuple
from datetime import datetime
import uuid

class JSONProcessor:
    """Handles streaming and chunking of large JSON files"""
    
    def __init__(self, chunk_size: int = 1000):
        """
        Initialize the JSON processor
        
        Args:
            chunk_size: Maximum number of items per chunk for arrays
        """
        self.chunk_size = chunk_size
    
    def _preprocess_json_file(self, file_path: str) -> str:
        """
        Preprocess JSON file to handle MongoDB export format
        by converting it to valid JSON.
        
        Args:
            file_path: Path to the original JSON file
            
        Returns:
            Path to the preprocessed JSON file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Try to parse as-is first
        try:
            json.loads(content)
            return file_path  # Already valid JSON
        except json.JSONDecodeError:
            pass
        
        # For MongoDB exports, try a more comprehensive approach
        try:
            # Handle MongoDB extended JSON format
            processed_content = self._convert_mongodb_to_json(content)
            
            # Create a temporary file with corrected JSON
            temp_file_path = file_path + '.temp'
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            # Verify the processed content is valid JSON
            json.loads(processed_content)
            return temp_file_path
            
        except Exception as e:
            # If all else fails, return original file and let the error bubble up
            return file_path
    
    def _convert_mongodb_to_json(self, content: str) -> str:
        """
        Convert MongoDB export format to valid JSON
        """
        # Step 1: Handle MongoDB functions
        content = re.sub(r'ObjectId\(["\']([^"\')]+)["\']\)', r'"\1"', content)
        content = re.sub(r'ISODate\(["\']([^"\')]+)["\']\)', r'"\1"', content)
        content = re.sub(r'NumberLong\(([^)]+)\)', r'\1', content)
        content = re.sub(r'NumberInt\(([^)]+)\)', r'\1', content)
        content = re.sub(r'NumberDecimal\(["\']([^"\')]+)["\']\)', r'\1', content)
        
        # Step 2: Fix unquoted keys (more comprehensive)
        content = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', content)
        
        # Step 3: Fix unquoted string values that look like UUIDs or IDs
        content = re.sub(r':\s*([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})([,}])', r': "\1"\2', content)
        content = re.sub(r':\s*([a-fA-F0-9]{24,})([,}])', r': "\1"\2', content)
        
        # Step 4: Convert single quotes to double quotes for string values
        content = re.sub(r"'([^']*?)'", r'"\1"', content)
        
        # Step 5: Handle boolean and null values (case-insensitive)
        content = re.sub(r'\btrue\b', 'true', content, flags=re.IGNORECASE)
        content = re.sub(r'\bfalse\b', 'false', content, flags=re.IGNORECASE)
        content = re.sub(r'\bnull\b', 'null', content, flags=re.IGNORECASE)
        
        return content

    def stream_json_file(self, file_path: str) -> Generator[Tuple[str, Any], None, None]:
        """
        Stream a JSON file and yield chunks of data
        
        Args:
            file_path: Path to the JSON file
            
        Yields:
            Tuple of (chunk_type, chunk_data) where chunk_type is a string
            identifying the type of chunk (e.g., 'day_wise', 'week_wise')
            and chunk_data is the actual data
        """
        temp_file_path = None
        try:
            # Preprocess the file to handle MongoDB/JavaScript object notation
            processed_file_path = self._preprocess_json_file(file_path)
            temp_file_path = processed_file_path if processed_file_path != file_path else None
            
            # Load the entire JSON file (since preprocessing already handled format issues)
            with open(processed_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process the loaded data
            if isinstance(data, dict):
                # Handle object at root level
                for chunk_type, chunk_data in self._process_dict_data(data):
                    yield chunk_type, chunk_data
            elif isinstance(data, list):
                # Handle array at root level - chunk it
                for i in range(0, len(data), self.chunk_size):
                    chunk = data[i:i + self.chunk_size]
                    yield 'root_chunk', chunk
            else:
                # Single value
                yield 'single_value', data
                
        except Exception as e:
            raise Exception(f"Error processing JSON file: {str(e)}")
        finally:
            # Clean up temporary file if created
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass  # Ignore cleanup errors
    
    def _process_dict_data(self, data: dict) -> Generator[Tuple[str, Any], None, None]:
        """
        Process a dictionary and yield chunks based on content
        """
        # Look for arrays that can be chunked
        for key, value in data.items():
            if isinstance(value, list) and len(value) > self.chunk_size:
                # Chunk large arrays
                for i in range(0, len(value), self.chunk_size):
                    chunk = value[i:i + self.chunk_size]
                    yield f'{key}_chunk_{i//self.chunk_size}', chunk
            else:
                # Yield smaller items as-is
                yield key, value
    
    def _process_object_legacy(self, parser, prefix: str) -> Generator[Tuple[str, Dict], None, None]:
        """Process a JSON object and yield chunks"""
        current_key = None
        chunk_buffer = []
        
        for prefix, event, value in parser:
            if event == 'map_key':
                current_key = value
            elif event == 'start_array' and current_key:
                # Process array values
                array_prefix = f"{prefix}.{current_key}"
                for chunk in self._process_array(parser, array_prefix, current_key):
                    yield current_key, chunk
            elif event == 'end_map' and prefix == '':
                # End of root object
                break
    
    def _process_array(self, parser, prefix: str, array_name: str) -> Generator[List[Dict], None, None]:
        """Process a JSON array and yield chunks of items"""
        chunk = []
        item_count = 0
        
        for event, value in ijson.parse(parser):
            if event == 'start_map':
                # Start of an object in the array
                item = {}
                current_key = None
                
                # Process object properties
                for prop_event, prop_value in parser:
                    if prop_event == 'map_key':
                        current_key = prop_value
                    elif prop_event in ('string', 'number', 'boolean', 'null'):
                        if current_key:
                            item[current_key] = prop_value
                    elif prop_event == 'end_map':
                        break
                
                # Add item to chunk
                chunk.append(item)
                item_count += 1
                
                # Yield chunk if size limit reached
                if len(chunk) >= self.chunk_size:
                    yield chunk
                    chunk = []
            
            elif event == 'end_array' and value == prefix:
                # End of the array
                if chunk:  # Yield any remaining items
                    yield chunk
                break
    
    def extract_metadata(self, chunk: Any, chunk_type: str) -> Dict[str, Any]:
        """
        Extract metadata from a chunk of data
        
        Args:
            chunk: Data chunk (can be list, dict, or other types)
            chunk_type: Type of the chunk (e.g., 'day_wise', 'week_wise')
            
        Returns:
            Dictionary containing metadata
        """
        if not chunk:
            return {}
        
        metadata = {
            'chunk_type': chunk_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Handle different chunk types
        if isinstance(chunk, list):
            metadata['item_count'] = len(chunk)
            if chunk and isinstance(chunk[0], dict):
                metadata['fields'] = list(chunk[0].keys())
            else:
                metadata['data_type'] = type(chunk[0]).__name__ if chunk else 'empty'
        elif isinstance(chunk, dict):
            metadata['item_count'] = 1
            metadata['fields'] = list(chunk.keys())
        else:
            metadata['item_count'] = 1
            metadata['data_type'] = type(chunk).__name__
        
        # Extract date range if available (only for list of dicts)
        if isinstance(chunk, list) and chunk and isinstance(chunk[0], dict):
            date_fields = ['date', 'timestamp', 'time', 'created_at', 'updated_at', 'start_date', 'end_date']
            for field in date_fields:
                if field in chunk[0]:
                    try:
                        dates = [item[field] for item in chunk if isinstance(item, dict) and field in item]
                        if dates:
                            metadata['date_range'] = {
                                'field': field,
                                'min': min(dates),
                                'max': max(dates)
                            }
                            break
                    except (TypeError, ValueError):
                        continue
        
        return metadata

    def create_chunk_id(self, source_file: str, chunk_type: str, index: int) -> str:
        """
        Create a unique ID for a chunk
        
        Args:
            source_file: Source file name
            chunk_type: Type of the chunk
            index: Chunk index
            
        Returns:
            Unique chunk ID
        """
        file_hash = str(hash(os.path.basename(source_file)))[-8:]
        return f"{file_hash}_{chunk_type}_{index}_{uuid.uuid4().hex[:8]}"
