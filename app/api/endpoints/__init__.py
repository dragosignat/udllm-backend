from fastapi import APIRouter
from app.api.endpoints.llm import router as llm_router
from app.api.endpoints.prompts import router as prompts_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.rlhf import router as rlhf_router
router = APIRouter()

# Include all routers with their respective prefixes
router.include_router(llm_router, prefix="/llm", tags=["LLM"])
router.include_router(prompts_router, prefix="/system-prompts", tags=["System Prompts"])
router.include_router(health_router, prefix="/health", tags=["Health"]) 
router.include_router(rlhf_router, prefix="/rlhf", tags=["RLHF"])