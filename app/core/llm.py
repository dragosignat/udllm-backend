from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.base.query_pipeline.query import QueryBundle
from qdrant_client import QdrantClient
from app.core.config import get_settings
from typing import List, Tuple
from pydantic import BaseModel
from detoxify import Detoxify

settings = get_settings()

class ArticleMetadata(BaseModel):
    title: str
    url: str

class LLMService:
    def __init__(self):
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=False)
        
        # Initialize vector store
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name="articles",
            text_key="content",
        )
        
        # Initialize embedding model
        self.embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
        
        # Initialize index
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=self.embed_model
        )
        
        # Initialize Ollama LLM
        self.llm = Ollama(
            model=settings.OLLAMA_MODEL,
            request_timeout=120.0,
            temperature=0.7,
            context_window=4096,
        )
        
        # Initialize query engine
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=10,
            llm=self.llm
        )

    def query(self, query: str, system_prompt: str) -> Tuple[str, List[ArticleMetadata]]:

        nodes = self.query_engine.retrieve(system_prompt + query)
        nodes = [node for node in nodes if node]

        if not nodes:
            return "No relevant content found.", []

        # Extract metadata from nodes
        articles = []
        for node in nodes:
            if hasattr(node, 'metadata') and node.metadata:
                metadata = node.metadata
                if 'title' in metadata and 'url' in metadata:
                    articles.append(ArticleMetadata(
                        title=metadata['title'],
                        url=metadata['url']
                    ))
            
        query_bundle = QueryBundle(query_str=system_prompt + query)
        response = self.query_engine.synthesize(nodes=nodes, query_bundle=query_bundle)
        print("LLM response: ", response)
        response = self._detoxify(str(response))
        print("Detoxified response: ", response)
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
        if any(value > 0.5 for value in toxicityResult.values()):
            toxicityResultString = ", ".join([f"{key} is {round(float(value), 2)}" for key, value in toxicityResult.items()])
            response = self.llm.complete(f"Toxicity analysis detected problematic content ({toxicityResultString}). Rewrite the following text using respectful language while preserving the essential meaning: {text}")
            return str(response)

        return text

llm_service = LLMService() 