# Saget's RFC

Blog técnico de telecomunicaciones con estética RFC.

## Descripción

Infraestructura, redes y virtualización desde el primer bit. Un blog personal para documentar proyectos, configuraciones y experiencias en telecomunicaciones, redes y tecnología.

## Características

- Diseño estilo RFC (Request for Comments)
- Tema claro/oscuro
- Panel de administración seguro
- Comentarios de lectores
- 100% español

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Templates**: Jinja2
- **Estética**: RFC-style con Font Awesome
- **Deployment**: Docker

## Instalación Local

```bash
# Instalar dependencias
cd backend
pip install -r requirements.txt

# Ejecutar en desarrollo
uvicorn app.main:app --reload
```

## Docker

```bash
# Build
docker build -t blog-tecnico ./backend

# Run
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data \
  -e SECRET_KEY=tu-secret-key \
  -e ADMIN_PASSWORD_HASH=tu-hash \
  blog-tecnico
```

## Docker Compose

```bash
# Copiar configuración
cp .env.example .env
# Editar .env con tus valores

# Iniciar
docker-compose up -d
```

## Estructura

```
backend/
├── app/
│   ├── main.py         # App FastAPI
│   ├── database.py    # SQLAlchemy config
│   ├── models.py      # Modelos DB
│   ├── schemas.py     # Pydantic schemas
│   ├── auth.py        # Auth utilities
│   ├── routers/       # API endpoints
│   ├── templates/     # Jinja2 templates
│   └── static/        # CSS
├── requirements.txt
└── Dockerfile

docker-compose.yml
.env.example
```

## Configuración

Variables de entorno en `.env`:

- `SECRET_KEY`: Secret para JWT (mínimo 32 caracteres)
- `ADMIN_USERNAME`: Usuario admin
- `ADMIN_PASSWORD_HASH`: Hash bcrypt del password
- `DATA_DIR`: Directorio para SQLite (default: /app/data)

## Deploy en producción

```bash
docker-compose up -d --build
```

## Licencia

MIT