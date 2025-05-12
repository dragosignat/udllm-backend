from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.schemas import PromptRequest, LLMResponse
from app.core.llm import llm_service
from app.core.prompt_service import PromptService
from app.core.satirical_llm import satirical_llm_service
from app.core.config import get_settings
import random

router = APIRouter()
settings = get_settings()

def _handle_satirical_llm(query: str):
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
    system_prompt = PromptService.get_favorite_prompt(db)
    
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