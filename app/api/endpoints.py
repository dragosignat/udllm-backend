from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.schemas import (
    PromptRequest, LLMResponse, QueryResponse,
    SystemPromptCreate, SystemPromptResponse
)
from app.core.llm import llm_service
from app.core.prompt_service import PromptService
from typing import List

router = APIRouter()

@router.post("/prompt", response_model=LLMResponse)
async def prompt_llm(request: PromptRequest, db: Session = Depends(get_db)):
    try:
        # Get a random system prompt
        system_prompt = PromptService.get_random_prompt(db)
        
        # Use the system prompt in the query
        response, articles = llm_service.query(
            f"{system_prompt.prompt}\n\n{request.prompt}",
            request.mode
        )
        
        return LLMResponse(
            response=response,
            mode=request.mode,
            prompt=request.prompt,
            articles=articles,
            system_prompt_id=system_prompt.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-prompts", response_model=SystemPromptResponse)
def create_system_prompt(prompt: SystemPromptCreate, db: Session = Depends(get_db)):
    try:
        return PromptService.add_prompt(db, prompt.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system-prompts/{prompt_id}/like", response_model=SystemPromptResponse)
def like_prompt(prompt_id: int, db: Session = Depends(get_db)):
    try:
        return PromptService.like_prompt(db, prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system-prompts/{prompt_id}/dislike", response_model=SystemPromptResponse)
def dislike_prompt(prompt_id: int, db: Session = Depends(get_db)):
    try:
        return PromptService.dislike_prompt(db, prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-prompts", response_model=List[SystemPromptResponse])
def get_prompt_stats(db: Session = Depends(get_db)):
    return PromptService.get_prompt_stats(db)

@router.get("/health")
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