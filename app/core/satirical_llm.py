from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.base.query_pipeline.query import QueryBundle
from qdrant_client import QdrantClient
from app.core.config import get_settings
from typing import List, Tuple, Optional
from pydantic import BaseModel
from app.core.llm import ArticleMetadata
from detoxify import Detoxify
settings = get_settings()


class SatiricalLLMService:
    def __init__(self):
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=False)
        
        # Initialize vector store for satirical articles
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name="satirical_articles",
            text_key="content",
        )
        
        # Initialize embedding model
        self.embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
        
        # Initialize index
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=self.embed_model
        )
        
        # Initialize Ollama LLM with higher temperature for more creative responses
        self.llm = Ollama(
            model=settings.OLLAMA_MODEL,
            request_timeout=120.0,
            temperature=0.9,  # Higher temperature for more creative/satirical responses
            context_window=4096,
        )
        
        # Initialize query engine
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=3,  # Reduced to get more focused results
            llm=self.llm
        )

    def generate_satirical_response(self, query: str, system_prompt: str = None, context: Optional[str] = None) -> Tuple[str, List[ArticleMetadata]]:
        """
        Generate a satirical response based on the user's query and relevant satirical articles.
        
        Args:
            query (str): The user's query
            system_prompt (str, optional): Additional context or instructions for the LLM
            
        Returns:
            Tuple[str, List[SatiricalArticleMetadata]]: The satirical response and list of referenced articles
        """
        # Construct a prompt that encourages satirical responses
        satirical_prompt = (
            "You are a witty and satirical AI assistant. "
            "Use the following context to create a humorous and satirical response "
            "while maintaining a light-hearted tone. "
            "Make sure to incorporate elements from the provided articles "
            "in a clever and entertaining way.\n\n"
            "Include emojis in your response to make it more engaging and fun"
        )
        
        if system_prompt:
            satirical_prompt += system_prompt + "\n\n"
        
        # Retrieve relevant nodes
        nodes = self.query_engine.retrieve(satirical_prompt + query)
        nodes = [node for node in nodes if node]

        if not nodes:
            return "I couldn't find any satirical inspiration for this topic. Maybe it's too serious?", []

        # Extract metadata from nodes
        articles = []
        for node in nodes:
            if hasattr(node, 'metadata') and node.metadata:
                metadata = node.metadata
                if 'title' in metadata and 'url' in metadata:
                    articles.append(ArticleMetadata(
                        title=metadata['title'],
                        url=metadata['url'],
                    ))
            
        query_bundle = QueryBundle(query_str=satirical_prompt + context + query)
        response = self.query_engine.synthesize(nodes=nodes, query_bundle=query_bundle)
        response = self._detoxify(str(response))
        
        return str(response), articles
    
    def _detoxify(self, text: str) -> str:
            """
            Detoxify the input text using the Detoxify library.

            Args:
                text (str): The input text to detoxify.

            Returns:
                str: The detoxified text.
            """
            detoxifier = Detoxify('original')
            toxicityResult = detoxifier.predict(text)
            if any(value > 0.6 for value in toxicityResult.values()):
                toxicityResultString = ", ".join([f"{key} is {round(float(value), 2)}" for key, value in toxicityResult.items()])
                response = self.llm.complete(f"Toxicity analysis detected problematic content ({toxicityResultString}). Rewrite the following text using respectful language while preserving the essential meaning and include emojis and keep the satirical and light-hearted tone: {text}")
                return str(response)

            return text


satirical_llm_service = SatiricalLLMService() 