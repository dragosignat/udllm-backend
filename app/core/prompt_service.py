from sqlalchemy.orm import Session
from app.models.models import SystemPrompt
from datetime import datetime
import random

class PromptService:
    @staticmethod
    def get_random_prompt(db: Session, other_prompt_ids: list[int] = []) -> SystemPrompt:
        # Get all prompts
        query = db.query(SystemPrompt)
        if other_prompt_ids:
            query = query.filter(SystemPrompt.id.notin_(other_prompt_ids))
        prompts = query.all()
        
        if not prompts:
            raise ValueError("No system prompts available")
        
        # Select a random prompt
        prompt = random.choice(prompts)
        
        # Update last_used
        prompt.last_used = datetime.now()
        prompt.used += 1
        db.commit()
        
        return prompt

    @staticmethod
    def add_prompt(db: Session, prompt_text: str) -> SystemPrompt:
        prompt = SystemPrompt(prompt=prompt_text)
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def like_prompt(db: Session, prompt_id: int) -> SystemPrompt:
        prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            raise ValueError("Prompt not found")
        prompt.likes += 1
        db.commit()
        return prompt

    @staticmethod
    def dislike_prompt(db: Session, prompt_id: int) -> SystemPrompt:
        prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            raise ValueError("Prompt not found")
        prompt.dislikes += 1
        db.commit()
        return prompt

    @staticmethod
    def get_prompt_stats(db: Session) -> list:
        return db.query(SystemPrompt).all() 