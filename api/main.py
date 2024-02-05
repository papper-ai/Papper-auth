from fastapi import FastAPI
from auth.auth_router import auth_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth_router)
