from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.schemas import (
    PromptRequest, LLMResponse, QueryResponse,
    SystemPromptCreate, SystemPromptResponse
)
from app.core.llm import llm_service
from app.core.prompt_service import PromptService
from app.core.satirical_llm import SatiricalLLMService
from app.core.config import get_settings
from typing import List
import random

router = APIRouter()
settings = get_settings()


def _handle_satirical_llm(query: str):
    satirical_llm_service = SatiricalLLMService()
    response, articles = satirical_llm_service.generate_satirical_response(query)

    return LLMResponse(
        response=response,
        mode="satirical",
        prompt=query,
        articles=articles,
        system_prompt_id=None
    )

def _handle_llm(query: str, db: Session):
     # Get a random system prompt
        system_prompt = PromptService.get_random_prompt(db)
        
        # Use the system prompt in the query
        response, articles = llm_service.query(
            query,
            system_prompt.prompt
        )
        
        # Check if we should return a second response
        if random.random() <= settings.MULTIPLE_PROMPT_PROB:
            # Get another random system prompt, excluding the first one
            second_system_prompt = PromptService.get_random_prompt(db, [system_prompt.id])
            
            # Get second response
            second_response, _ = llm_service.query(
                query,
                second_system_prompt.prompt
            )
            
            return LLMResponse(
                response=response,
                mode="normal",
                prompt=query,
                articles=articles,
                system_prompt_id=system_prompt.id,
                second_response=second_response,
                second_system_prompt_id=second_system_prompt.id
            )
        
        return LLMResponse(
        response=response,
        mode="normal",
        prompt=query,
        articles=articles,
        system_prompt_id=system_prompt.id
        )


@router.post("/prompt", response_model=LLMResponse)
async def prompt_llm(request: PromptRequest, db: Session = Depends(get_db)):
    try:
        if request.mode == "satirical":
            return _handle_satirical_llm(request.prompt)
        else:
            return _handle_llm(request.prompt, db)
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

