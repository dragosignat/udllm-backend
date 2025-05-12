from app.core.config import get_settings
from app.core.kafka_service import kafka_service, RLHFMessage
from fastapi import APIRouter, HTTPException
settings = get_settings()

router = APIRouter()

@router.post("/reward")
async def reward(message: RLHFMessage):
    try:
        kafka_service.send_message(settings.KAFKA_TOPIC, message)
        return {"message": "Reward sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
