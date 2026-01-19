from app.routes.users import router as user_routes
from app.routes.health import router as health_route
from app.routes.clients import router as client_routes
from app.routes.upload import router as upload_routes
from app.routes.contracts import router as contract_routes
from app.routes.products import router as product_routes

def register_routes(app):
    app.include_router(user_routes)
    app.include_router(health_route)
    app.include_router(client_routes)
    app.include_router(upload_routes)
    app.include_router(contract_routes)
    app.include_router(product_routes)

