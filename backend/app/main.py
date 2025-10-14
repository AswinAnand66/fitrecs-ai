from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import auth, items, recommend, interactions
from .db.session import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)
app.include_router(
    items.router,
    prefix=f"{settings.API_V1_STR}/items",
    tags=["items"]
)
app.include_router(
    recommend.router,
    prefix=f"{settings.API_V1_STR}/recommend",
    tags=["recommend"]
)
app.include_router(
    interactions.router,
    prefix=f"{settings.API_V1_STR}/interactions",
    tags=["interactions"]
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()