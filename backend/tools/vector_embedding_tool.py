from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional
from tools.supabase_client import supabase
from tools.supabase_admin_client import admin_supabase
from config.logging_config import setup_logging
import openai
import os
import json
import traceback
from datetime import datetime

logger = setup_logging()

class VectorEmbeddingTool(BaseTool):
    name: str = "vector_embedding_tool"
    description: str = "Create and manage vector embeddings for blog posts in Supabase"
    
    def _run(self, blog_id: str = None, content: str = None, title: str = None, operation: str = "create") -> Dict[str, Any]:
        """
        Create, retrieve, or search vector embeddings for blog posts
        
        Args:
            blog_id: The ID of the blog post
            content: The content to embed (for create operation)
            title: The title of the blog post (for create operation)
            operation: The operation to perform (create, retrieve, search)
            
        Returns:
            A dictionary with the result of the operation
        """
        try:
            if operation == "create" and content and blog_id:
                return self._create_embeddings(blog_id, content, title)
            elif operation == "retrieve" and blog_id:
                return self._retrieve_embeddings(blog_id)
            elif operation == "search" and content:
                return self._search_embeddings(content)
            else:
                return {"error": "Invalid operation or missing parameters"}
        except Exception as e:
            logger.error(f"Error in vector_embedding_tool: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _create_embeddings(self, blog_id: str, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Create embeddings for a blog post and store them in Supabase"""
        try:
            # Check if the blog post exists
            blog_result = supabase.table('blogs').select('*').eq('id', blog_id).execute()
            
            if not blog_result.data:
                return {"error": f"Blog post with ID {blog_id} not found"}
            
            # Generate embeddings using OpenAI
            embedding = self._generate_embedding(content)
            
            if not embedding:
                return {"error": "Failed to generate embedding"}
            
            # Prepare the data for Supabase
            embedding_data = {
                "blog_id": blog_id,
                "content": content[:1000],  # Store a preview of the content
                "title": title or blog_result.data[0].get('title', ''),
                "embedding": embedding,
                "created_at": datetime.now().isoformat()
            }
            
            # Try to insert into Supabase
            try:
                # First try with regular client
                result = supabase.table('blog_embeddings').insert(embedding_data).execute()
                logger.info(f"Created embedding for blog ID: {blog_id}")
            except Exception as e:
                logger.warning(f"Error inserting embedding with regular client: {str(e)}")
                # Try with admin client
                if admin_supabase:
                    result = admin_supabase.table('blog_embeddings').insert(embedding_data).execute()
                    logger.info(f"Created embedding for blog ID: {blog_id} using admin client")
                else:
                    raise Exception("Admin client not available and regular client failed")
            
            return {
                "status": "success",
                "message": f"Created embedding for blog ID: {blog_id}",
                "blog_id": blog_id
            }
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _retrieve_embeddings(self, blog_id: str) -> Dict[str, Any]:
        """Retrieve embeddings for a blog post from Supabase"""
        try:
            result = supabase.table('blog_embeddings').select('*').eq('blog_id', blog_id).execute()
            
            if not result.data:
                return {"error": f"No embeddings found for blog ID: {blog_id}"}
            
            return {
                "status": "success",
                "embeddings": result.data,
                "blog_id": blog_id
            }
            
        except Exception as e:
            logger.error(f"Error retrieving embeddings: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _search_embeddings(self, query: str) -> Dict[str, Any]:
        """Search for blog posts using vector similarity"""
        try:
            # Generate embedding for the query
            query_embedding = self._generate_embedding(query)
            
            if not query_embedding:
                return {"error": "Failed to generate embedding for query"}
            
            # Perform vector similarity search in Supabase
            # Using the match_documents RPC function that needs to be created in Supabase
            try:
                result = supabase.rpc(
                    'match_blog_embeddings', 
                    {
                        'query_embedding': query_embedding,
                        'match_threshold': 0.5,
                        'match_count': 5
                    }
                ).execute()
                
                if not result.data:
                    return {"error": "No matching blog posts found"}
                
                return {
                    "status": "success",
                    "matches": result.data
                }
                
            except Exception as e:
                logger.error(f"Error performing vector search: {str(e)}")
                return {"error": f"Vector search failed: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Error searching embeddings: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for the given text using OpenAI"""
        try:
            # Ensure API key is set
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            # Generate embedding
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            # Extract the embedding
            embedding = response.data[0].embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def _parse_input(self, inputs: Any) -> Dict[str, Any]:
        """Parse the input to extract blog_id, content, title, and operation"""
        logger.info(f"vector_embedding_tool received inputs type: {type(inputs)}")
        
        # Default values
        blog_id = None
        content = None
        title = None
        operation = "create"
        
        # Extract from dictionary inputs
        if isinstance(inputs, dict):
            # Log all keys to help with debugging
            logger.info(f"Input keys: {list(inputs.keys())}")
            
            blog_id = inputs.get('blog_id')
            content = inputs.get('content')
            title = inputs.get('title')
            operation = inputs.get('operation', 'create')
            
            # Handle nested inputs
            if 'inputs' in inputs and isinstance(inputs['inputs'], dict):
                nested_inputs = inputs['inputs']
                logger.info(f"Nested input keys: {list(nested_inputs.keys())}")
                
                if not blog_id:
                    blog_id = nested_inputs.get('blog_id')
                if not content:
                    content = nested_inputs.get('content')
                if not title:
                    title = nested_inputs.get('title')
                if 'operation' in nested_inputs:
                    operation = nested_inputs.get('operation')
        
        return {
            "blog_id": blog_id,
            "content": content,
            "title": title,
            "operation": operation
        }

# Create an instance of the tool
vector_embedding_tool = VectorEmbeddingTool() 