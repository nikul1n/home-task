from fastapi import FastAPI   # , APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, users
from app.api.v1.endpoints import boards

app = FastAPI(
    title="FastAPI JWT Auth Demo",
    description="Пример реализации JWT авторизации на FastAPI",
    version="1.0.0"
)

# CORS для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роутеры
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(boards.router, prefix="/api/v1/boards", tags=["boards"]) #f"{settings.API_V1_STR}/boards", tags=["boards"])

@app.get("/")
async def root():
    return {"message": "FastAPI JWT Auth Demo. Go to /docs for API documentation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

