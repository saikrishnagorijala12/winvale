from app.routes.users import router as user_routes
from app.routes.health import router as health

def register_routes(app):
    app.include_router(user_routes)
    app.include_router(health)
