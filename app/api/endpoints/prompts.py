from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.schemas import SystemPromptCreate, SystemPromptResponse
from app.core.prompt_service import PromptService
from typing import List

router = APIRouter()

@router.post("", response_model=SystemPromptResponse)
def create_system_prompt(prompt: SystemPromptCreate, db: Session = Depends(get_db)):
    try:
        return PromptService.add_prompt(db, prompt.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{prompt_id}/like", response_model=SystemPromptResponse)
def like_prompt(prompt_id: int, db: Session = Depends(get_db)):
    try:
        return PromptService.like_prompt(db, prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{prompt_id}/dislike", response_model=SystemPromptResponse)
def dislike_prompt(prompt_id: int, db: Session = Depends(get_db)):
    try:
        return PromptService.dislike_prompt(db, prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[SystemPromptResponse])
def get_prompt_stats(db: Session = Depends(get_db)):
    return PromptService.get_prompt_stats(db) 