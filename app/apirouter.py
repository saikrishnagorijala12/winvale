from app.routes.users import router as user_routes

def register_routes(app):
    app.include_router(user_routes)