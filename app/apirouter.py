from app.routes.test import router as test_routes
from app.routes.test2 import router as test2_routes

def register_routes(app):
    app.include_router(test_routes, prefix="")
    app.include_router(test2_routes, prefix="")