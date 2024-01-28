from fastapi import FastAPI
import uvicorn
from auth.auth_router import auth_router

app = FastAPI()

app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)