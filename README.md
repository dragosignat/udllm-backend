# UDLLM Backend

A FastAPI-based backend service for querying news articles using Large Language Models (LLM). This service provides a robust API for natural language processing and article analysis.

## 🚀 Features

- FastAPI-based REST API
- LLM-powered article querying
- Kafka integration for event streaming
- SQLAlchemy for database operations
- CORS enabled for cross-origin requests
- Docker support for easy deployment

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy
- **Message Broker**: Apache Kafka
- **Containerization**: Docker
- **Python Version**: 3.11

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11 (if running locally)
- Git

## 🚀 Getting Started

### Using Docker (Recommended)

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd udllm-backend
   ```

2. Start the services using Docker Compose:

   ```bash
   docker-compose up -d
   ```

3. The API will be available at `http://localhost:8000`

### Local Development

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirments.txt
   ```

3. Run the application:
   ```bash
   fastapi dev main.py
   ```
4. Run the Qdrant server and Kafka broker:
   ```bash
   docker-compose up -d
   ```

## 📚 API Documentation

Once the application is running, you can access:

- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## 🏗️ Project Structure

```
udllm-backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configurations
│   ├── database/     # Database configurations
│   └── models/       # Database models
├── main.py           # Application entry point
├── Dockerfile        # Docker configuration
├── docker-compose.yml # Docker services configuration
└── requirments.txt   # Python dependencies
```

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```env
# Add your environment variables here
```

## 🐳 Docker Services

The project includes the following Docker services:

- FastAPI application
- Kafka message broker

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- FastAPI documentation
- Apache Kafka documentation
- SQLAlchemy documentation
