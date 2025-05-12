from kafka import KafkaProducer
from app.core.config import get_settings
from app.api.schemas import RLHFMessage

settings = get_settings()

class KafkaService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER
        )
        
    def send_message(self, topic: str, message: RLHFMessage):
        try:
            print(f"Sending message to {topic}: {message}")
            self.producer.send(topic, message.model_dump_json().encode('utf-8'))
            self.producer.flush()
        except Exception as e:
            print(f"Error sending message to {topic}: {e}")

kafka_service = KafkaService()