from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional
from tools.supabase_client import supabase
from tools.vector_embedding_tool import vector_embedding_tool
from config.logging_config import setup_logging
import openai
import os
import json
import traceback
from datetime import datetime

logger = setup_logging()

class RAGTool(BaseTool):
    name: str = "rag_tool"
    description: str = "Retrieve and generate answers using RAG (Retrieval Augmented Generation)"
    
    def _run(self, query: str = None, blog_id: str = None, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate answers using RAG based on the query and blog post
        
        Args:
            query: The user's query
            blog_id: The ID of the blog post to use as context (optional)
            chat_history: The chat history (optional)
            
        Returns:
            A dictionary with the generated answer
        """
        try:
            if not query:
                return {"error": "Query is required"}
            
            # Initialize chat history if not provided
            if not chat_history:
                chat_history = []
            
            # Retrieve relevant context
            context = self._retrieve_context(query, blog_id)
            
            if "error" in context:
                return context
            
            # Generate answer using the context
            answer = self._generate_answer(query, context, chat_history)
            
            return {
                "status": "success",
                "answer": answer,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error in rag_tool: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _retrieve_context(self, query: str, blog_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve relevant context for the query"""
        try:
            # If blog_id is provided, retrieve that specific blog post
            if blog_id:
                blog_result = supabase.table('blogs').select('*').eq('id', blog_id).execute()
                
                if not blog_result.data:
                    return {"error": f"Blog post with ID {blog_id} not found"}
                
                blog_post = blog_result.data[0]
                
                return {
                    "blog_posts": [blog_post],
                    "source": "specific_blog"
                }
            
            # Otherwise, perform a vector search
            search_result = vector_embedding_tool._search_embeddings(query)
            
            if "error" in search_result:
                # Fallback to keyword search if vector search fails
                logger.warning(f"Vector search failed, falling back to keyword search: {search_result['error']}")
                
                # Simple keyword search in blog titles and content
                keyword_result = supabase.table('blogs').select('*').filter(
                    f"title.ilike.%{query}%", 
                    f"content.ilike.%{query}%"
                ).limit(5).execute()
                
                if not keyword_result.data:
                    return {"error": "No relevant blog posts found"}
                
                return {
                    "blog_posts": keyword_result.data,
                    "source": "keyword_search"
                }
            
            # Get the full blog posts for the matched embeddings
            blog_ids = [match['blog_id'] for match in search_result['matches']]
            
            if not blog_ids:
                return {"error": "No matching blog posts found"}
            
            blogs_result = supabase.table('blogs').select('*').in_('id', blog_ids).execute()
            
            if not blogs_result.data:
                return {"error": "Failed to retrieve blog posts"}
            
            return {
                "blog_posts": blogs_result.data,
                "source": "vector_search"
            }
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": f"Failed to retrieve context: {str(e)}"}
    
    def _generate_answer(self, query: str, context: Dict[str, Any], chat_history: List[Dict[str, str]]) -> str:
        """Generate an answer using the context and chat history"""
        try:
            # Ensure API key is set
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            # Prepare the context
            blog_posts = context.get('blog_posts', [])
            
            if not blog_posts:
                return "I couldn't find any relevant information to answer your question."
            
            # Format the context
            context_text = ""
            for i, post in enumerate(blog_posts):
                context_text += f"Blog {i+1}: {post.get('title', 'Untitled')}\n"
                context_text += f"Content: {post.get('content', 'No content')[:1000]}...\n\n"
            
            # Format the chat history
            history_text = ""
            for message in chat_history[-5:]:  # Only use the last 5 messages
                role = message.get('role', 'user')
                content = message.get('content', '')
                history_text += f"{role.capitalize()}: {content}\n"
            
            # Create the prompt
            system_prompt = """You are TrendSage Assistant, an AI that helps users understand trends and insights from blog posts.
            Use the provided blog content to answer the user's question accurately and informatively.
            If the information is not in the provided context, acknowledge that and provide general information if possible.
            Always be helpful, concise, and accurate."""
            
            user_prompt = f"""
            Question: {query}
            
            Context from relevant blog posts:
            {context_text}
            
            Previous conversation:
            {history_text}
            
            Please provide a helpful answer based on the context provided.
            """
            
            # Generate the answer
            response = openai.chat.completions.create(
                model=os.getenv('OPENAI_MODEL_NAME', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            logger.error(traceback.format_exc())
            return f"I'm sorry, I encountered an error while generating an answer: {str(e)}"
    
    def _parse_input(self, inputs: Any) -> Dict[str, Any]:
        """Parse the input to extract query, blog_id, and chat_history"""
        logger.info(f"rag_tool received inputs type: {type(inputs)}")
        
        # Default values
        query = None
        blog_id = None
        chat_history = []
        
        # Extract from dictionary inputs
        if isinstance(inputs, dict):
            # Log all keys to help with debugging
            logger.info(f"Input keys: {list(inputs.keys())}")
            
            query = inputs.get('query')
            blog_id = inputs.get('blog_id')
            chat_history = inputs.get('chat_history', [])
            
            # Handle nested inputs
            if 'inputs' in inputs and isinstance(inputs['inputs'], dict):
                nested_inputs = inputs['inputs']
                logger.info(f"Nested input keys: {list(nested_inputs.keys())}")
                
                if not query:
                    query = nested_inputs.get('query')
                if not blog_id:
                    blog_id = nested_inputs.get('blog_id')
                if not chat_history and 'chat_history' in nested_inputs:
                    chat_history = nested_inputs.get('chat_history', [])
        
        # If input is a string, treat it as the query
        elif isinstance(inputs, str):
            query = inputs
        
        return {
            "query": query,
            "blog_id": blog_id,
            "chat_history": chat_history
        }

# Create an instance of the tool
rag_tool = RAGTool()
