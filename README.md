# PostMorph AI

A platform to convert Instagram Reels to LinkedIn posts.

## Tech Stack
- Backend: FastAPI, PostgreSQL, SQLAlchemy, Celery, Redis
- Frontend: React, Vite, TailwindCSS
- Infrastructure: Docker, Docker Compose

## Getting Started

1. Clone the repository.
2. Copy `backend/.env.example` to `backend/.env` and fill in your API keys (Deepgram, Gemini, Instagram, LinkedIn).
3. Ensure FFmpeg is installed on your system.
4. Run `docker-compose up --build` or run locally.

## Services
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379
