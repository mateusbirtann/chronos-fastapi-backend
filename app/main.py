from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware

app = FastAPI(title=settings.PROJECT_NAME)

setup_middleware(app)
setup_logging()

app.include_router(router)
