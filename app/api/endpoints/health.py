from fastapi import APIRouter, HTTPException
from app.core.llm import llm_service

router = APIRouter()

@router.get("")
async def health_check():
    try:
        # Test vector store connection
        llm_service.vector_store._client.get_collection(llm_service.vector_store.collection_name)
        return {
            "status": "healthy",
            "model": llm_service.llm.model,
            "vector_store": "connected",
            "embedding_model": llm_service.embed_model.model_name
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}") 