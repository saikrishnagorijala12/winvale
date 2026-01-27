# import uvicorn
from app import create_app
from fastapi.middleware.cors import CORSMiddleware
 
app = create_app()
 
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)