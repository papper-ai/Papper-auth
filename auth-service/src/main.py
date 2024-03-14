from fastapi import FastAPI
from auth.router import auth_router
import uvicorn

app = FastAPI()
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

