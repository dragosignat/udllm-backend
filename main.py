from fastapi import FastAPI, HTTPException
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.base.query_pipeline.query import QueryBundle
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List

# CONFIG
QDRANT_URL = "http://100devs.sogard.ro:6333"
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
OLLAMA_MODEL = "mistral"  # or any other model you have in Ollama

# Initialize FastAPI app
app = FastAPI()

# Initialize components
try:
    # Initialize Qdrant client
    qdrant_client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)
    
    # Initialize vector store
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="articles",
        text_key="content",
    )
    
    # Initialize embedding model
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    
    # Initialize index
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model
    )
    
    # Initialize Ollama LLM
    llm = Ollama(
        model=OLLAMA_MODEL,
        request_timeout=120.0,
        temperature=0.7,
        context_window=4096,
    )
    
    # Initialize query engine
    query_engine = index.as_query_engine(
        similarity_top_k=10,
        llm=llm
    )
    
except Exception as e:
    print(f"Initialization error: {str(e)}")
    raise

class ArticleMetadata(BaseModel):
    title: str
    url: str

class PromptRequest(BaseModel):
    prompt: str
    mode: str = "qa"  # Can be "qa" or "summarize"
    temperature: Optional[float] = 0.7

class LLMResponse(BaseModel):
    response: str
    mode: str
    prompt: str
    articles: List[ArticleMetadata]

@app.get("/")
def read_root():
    return {"status": "API is running"}

def rag_query(query: str, mode: str = "qa") -> tuple[str, List[ArticleMetadata]]:
    try:
        if mode == "summarize":
            system_prompt = "Summarize the following news snippets:\n\n"
        else:
            system_prompt = "Answer based on these news snippets:\n\n"

        nodes = query_engine.retrieve(system_prompt + query)
        nodes = [node for node in nodes if node]

        if not nodes:
            return "No relevant content found.", []

        # Extract metadata from nodes
        articles = []
        for node in nodes:
            # Try to extract from payload
            if hasattr(node, 'metadata') and node.metadata:
                metadata = node.metadata
                if 'title' in metadata and 'url' in metadata:
                    articles.append(ArticleMetadata(
                        title=metadata['title'],
                        url=metadata['url']
                    ))
            
        query_bundle = QueryBundle(query_str=system_prompt + query)
        response = query_engine.synthesize(nodes=nodes, query_bundle=query_bundle)
        return str(response), articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@app.post("/prompt", response_model=LLMResponse)
async def prompt_llm(request: PromptRequest):
    try:
        response, articles = rag_query(request.prompt, request.mode)
        return LLMResponse(
            response=response,
            mode=request.mode,
            prompt=request.prompt,
            articles=articles
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        # Test vector store connection
        vector_store._client.get_collection(vector_store.collection_name)
        return {
            "status": "healthy",
            "model": OLLAMA_MODEL,
            "vector_store": "connected",
            "embedding_model": EMBEDDING_MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

