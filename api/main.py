from fastapi import FastAPI
from auth.auth_router import auth_router

app = FastAPI()

app.include_router(auth_router)
