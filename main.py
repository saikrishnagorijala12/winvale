# import uvicorn
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from app import create_app

from app.config import settings

app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    origin = f"{request.url.scheme}://{request.url.hostname}"
    if request.url.port:
        origin += f":{request.url.port}"

    csp_script_src = " ".join(settings.CSP_SCRIPT_SRC)
    csp_style_src = " ".join(settings.CSP_STYLE_SRC)
    csp_img_src = " ".join(settings.CSP_IMG_SRC)

    csp = (
        f"default-src 'self'; "
        f"script-src {csp_script_src}; "
        f"style-src {csp_style_src}; "
        f"img-src {csp_img_src}; "
        "font-src 'self' data:; "
        f"connect-src 'self' {origin}; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"

    return response


@app.get("/")
def greet():
    return settings.APP_GREET_MESSAGE


# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)