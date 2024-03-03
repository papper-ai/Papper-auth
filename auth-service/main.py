from fastapi import FastAPI
from src.auth.router import auth_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth_router)
