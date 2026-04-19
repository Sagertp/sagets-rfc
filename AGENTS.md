# AGENTS.md

## Project Structure
- `backend/`: Blog Técnico - FastAPI + SQLite + Jinja2
  - `Dockerfile`: Container definition
  - `requirements.txt`: Python dependencies
  - `app/`: Application code (main, models, routers, templates, static)
- `firmware/`: ESP32-S3 (planned)
- `.agent_context/`: Agent memory and state files

## Stack
- **Backend**: FastAPI 0.115, SQLAlchemy 2.0, SQLite
- **Templates**: Jinja2 con estética RFC + OpenCode docs
- **Auth**: JWT + bcrypt (password hasheado)
- **Deployment**: Docker + docker-compose

## Workflow
1. **Write tests first** (Pytest) before implementation
2. **Avoid full rewrites** - send diffs with line/function references
3. **Memory checkpoint** - update `LAST_MILE_STATE.md` at 80% context usage

## Commands
```bash
# Build and run
docker build -t blog-tecnico ./backend
docker-compose up -d

# Development (needs Python with pip)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables
- `SECRET_KEY`: JWT secret (min 32 chars)
- `ADMIN_USERNAME`: Username para admin
- `ADMIN_PASSWORD_HASH`: Hash bcrypt del password
- `DATA_DIR`: Directorio para SQLite (default: /app/data)

## Key Constraints
- Follow ISO 25010 and clean code standards
- Preserve context by avoiding redundant file rewrites